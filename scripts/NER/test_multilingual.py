import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import classification_report
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import pickle

# Choose cpu or gpu
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# Process data
def read_wikiner_data(filename):
    sentences = []
    sentence = []

    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                if sentence:
                    sentences.append(sentence)
                    sentence = []
            else:
                word, tag = line.split()
                sentence.append(
                    (word, tag.replace("B-", "").replace("I-", "").replace("MISC", "O")))
        if sentence:
            sentences.append(sentence)

    return sentences


def read_conll_data(filepath):
    sentences, labels = [], []
    with open(filepath, "r", encoding="utf-8") as f:
        sentence, label = [], []
        for line in f:
            if line.strip() == "":
                if sentence:
                    sentences.append(sentence)
                    sentence = []
            else:
                parts = line.strip().split()
                sentence.append(
                    (parts[0], parts[-1].replace("B-", "").replace("I-", "").replace("MISC", "O")))
        if sentence:
            sentences.append(sentence)
    return sentences


# choose the data to evaluate on
# data = read_wikiner_data('./wikiner/test_corpus_aij_wikiner_wp3.txt')
# data = read_wikiner_data('./wikiner-fr/test_corpus_aij_wikiner_wp3_fr.txt')
data = read_conll_data('./conll/test.txt')

# Load word2idx and tag2idx
with open("./entityTag/word2idx.pkl", "rb") as f:
    word2idx = pickle.load(f)
with open("./entityTag/tag2idx.pkl", "rb") as f:
    tag2idx = pickle.load(f)
idx2word = {i: w for w, i in word2idx.items()}
idx2tag = {i: t for t, i in tag2idx.items()}
max_length = max(len(sentence) for sentence in data)


class NERDataset(Dataset):
    def __init__(self, data, word2idx, tag2idx, max_length):
        self.data = data
        self.word2idx = word2idx
        self.tag2idx = tag2idx
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sentence = self.data[idx]
        words = [word for word, _ in sentence]
        tags = [tag for _, tag in sentence]

        word_indices = [self.word2idx.get(
            word, self.word2idx["<UNK>"]) for word in words]
        tag_indices = [self.tag2idx[tag] for tag in tags]

        length = len(words)
        padded_words = word_indices + \
            [self.word2idx["<PAD>"]] * (self.max_length - length)
        padded_tags = tag_indices + \
            [self.tag2idx["<PAD>"]] * (self.max_length - length)

        return torch.tensor(padded_words), torch.tensor(padded_tags)


test_dataset = NERDataset(data, word2idx, tag2idx, max_length)
test_dataloader = DataLoader(test_dataset, batch_size=128, shuffle=False)


# Model structure
class SelfAttentionLayer(nn.Module):
    def __init__(self, feature_size):
        super(SelfAttentionLayer, self).__init__()
        self.feature_size = feature_size
        # Q, K, V
        self.key = nn.Linear(feature_size, feature_size)
        self.query = nn.Linear(feature_size, feature_size)
        self.value = nn.Linear(feature_size, feature_size)

    def forward(self, x, mask=None):
        keys = self.key(x)
        queries = self.query(x)
        values = self.value(x)

        scores = torch.matmul(queries, keys.transpose(-2, -1)) / \
            torch.sqrt(torch.tensor(self.feature_size, dtype=torch.float32))

        if mask is not None:
            scores = scores.masked_fill(
                mask == 0, -1e9)  # apply mask to scores
        attention_weights = F.softmax(scores, dim=-1)
        output = torch.matmul(attention_weights, values)

        return output, attention_weights


class LSTM_NER(nn.Module):
    def __init__(self, vocab_size, tagset_size, embed_dim=200, hidden_dim=256):
        super(LSTM_NER, self).__init__()
        self.hidden_dim = hidden_dim
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers=2,
                            dropout=0.5, batch_first=True, bidirectional=True)
        self.attention = SelfAttentionLayer(2 * hidden_dim)
        self.fc = nn.Linear(2 * hidden_dim, tagset_size)

    def forward(self, x, mask=None):
        x = self.embedding(x)
        x, _ = self.lstm(x)
        x, _ = self.attention(x, mask)
        x = self.fc(x)
        return x


model = LSTM_NER(vocab_size=len(word2idx), tagset_size=len(tag2idx)).to(device)
model.load_state_dict(torch.load("best_model.pth"))
model.eval()


def evaluate_model(model, dataloader):
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for words, tags in dataloader:
            words, tags = words.to(device), tags.to(device)

            # Forward pass
            outputs = model(words)
            _, predicted_tags = torch.max(outputs, dim=2)

            # Flatten the predictions and tags for evaluation
            all_preds.extend(predicted_tags.view(-1).cpu().numpy())
            all_labels.extend(tags.view(-1).cpu().numpy())

    # Remove padding values for evaluation
    mask = np.array(all_labels) != tag2idx["<PAD>"]
    all_preds = np.array(all_preds)[mask]
    all_labels = np.array(all_labels)[mask]

    with open("res.txt", "w") as f:
        for i in range(len(all_preds)):
            f.write(f"{idx2tag[all_preds[i]]}, {idx2tag[all_labels[i]]}")
            f.write("\n")

    # Exclude the padding tag for the classification report
    target_names = [tag for tag in idx2tag.values() if tag != "<PAD>"]
    labels = [tag2idx[tag] for tag in target_names]

    # Print classification report (F1-score by label)
    print(classification_report(all_labels, all_preds,
          target_names=target_names, labels=labels))


# Evaluate the model
evaluate_model(model, test_dataloader)
