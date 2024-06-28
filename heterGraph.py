from torch_geometric.datasets import OGB_MAG
import torch_geometric.transforms as T

dataset = OGB_MAG(root='./data', preprocess='metapath2vec', transform=T.ToUndirected())
data = dataset[0]

from torch_geometric.nn import SAGEConv, to_hetero
import torch
import torch.nn.functional as F

device = torch.device('cuda')


class GNN(torch.nn.Module):
    def __init__(self, hidden_channels, out_channels):
        super().__init__()
        self.conv1 = SAGEConv((-1, -1), hidden_channels)
        self.conv2 = SAGEConv((-1, -1), out_channels)
    
    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        x = self.conv2(x, edge_index)
        return x


model = GNN(hidden_channels=64, out_channels=dataset.num_classes)
model = to_hetero(model, data.metadata(), aggr='sum')
optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)

model = model.to(device)
from torch_geometric.loader import HGTLoader

loader = HGTLoader(data,
                   # Sample 2048 nodes per type and per iteration for 4 iterations
                   num_samples={key: [2048] * 4 for key in data.node_types},
                   batch_size=32768, shuffle=True,
                   input_nodes=('paper', data['paper'].train_mask),
                   )  # Adjust batch_size as needed
data = model.to(device)


def train(data):
    model.train()
    optimizer.zero_grad()
    out = model(data.x_dict, data.edge_index_dict)
    mask = data['paper'].train_mask
    loss = F.cross_entropy(out['paper'][mask], data['paper'].y[mask])
    loss.backward()
    optimizer.step()
    return float(loss)


if __name__ == '__main__':
    for i in range(100):
        for batch in loader:
            loss = train(batch.to(device))
            print(f"{i}: {loss}")
