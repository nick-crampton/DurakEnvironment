import torch
import torch.nn as nn
import torch.nn.functional as F
from durakNew.playerTypes.DQN import agentDQN

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def convertToTensor(state):

    stateTensor = torch.tensor(state, dtype = torch.float)
    print(len(stateTensor))
    return stateTensor

class DQN(nn.Module):
    def __init__(self, inputSize, outputSize):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(inputSize, 1024)
        self.fc2 = nn.Linear(1024, 768)
        self.fc3 = nn.Linear(768, 512) 
        self.out = nn.Linear(512, outputSize)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = self.out(x)
        return x
    
def trainNetwork(model, replayBuffer, batchSize):
    if len(replayBuffer) < batchSize:
        return
    
    batch = random.sample(replayBuffer, batchSize)

    states = torch.tensor([b[0] for b in batch], dtype=torch.float, device=device)
    actions = torch.tensor([b[1] for b in batch], dtype=torch.long, device=device)
    rewards = torch.tensor([b[2] for b in batch], dtype=torch.float, device=device)
    futureStates = torch.tensor([b[3] for b in batch], dtype=torch.float, device=device)
    T = torch.tensor([b[4] for b in batch], dtype=torch.float, device=device)

    outputTensor = model(states)
    actionSelected = actions.unsqueeze(-1)
    currentQ = outputTensor.gather(1, actionSelected).squeeze(-1)
    
    nextQ = model(futureStates).detach().max(1)[0]

    targetQ = rewards + (gamma * nextQ * (1 - T))

    loss = F.mse_loss(currentQ, targetQ)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

model = DQN(inputSize=1374, outputSize=425).to(device)
optimizer = optim.Adam(model.parameters(), lr=0.001)

