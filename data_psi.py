import json
from transformers import BertTokenizer
from torch_geometric.nn import SAGEConv
import torch
from torch_geometric.data import Data


class GNN(torch.nn.Module):
    def __init__(self, hidden_channels, out_channels):
        super().__init__()
        self.conv1 = SAGEConv((-1, -1), hidden_channels)
        self.conv2 = SAGEConv((-1, -1), out_channels)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        x = self.conv2(x, edge_index)
        return x


tokenizer = BertTokenizer.from_pretrained('bert-base-cased')


def text2vec(_text: str):
    return tokenizer(_text, return_attention_mask=False)


if __name__ == '__main__':
    with open("bugs_psi/AaltoXml_1b-all.json") as f:
        psi = json.load(f)
    encoded_input = text2vec("x")
    print(encoded_input)
    model = GNN(hidden_channels=64, out_channels=16)
    data = Data()
    nodes = [[int(n['id']), ] for n in psi['nodes']]
