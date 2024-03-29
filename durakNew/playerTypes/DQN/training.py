import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import random
from durakNew.playerTypes.DQN import agentDQN
from durakNew.playerTypes.DQN import replayBuffer

def convertToTensor(state):

    stateTensor = torch.tensor(state, dtype = torch.float)
    return stateTensor

class DQN(nn.Module):
    def __init__(self, inputSize, outputSize):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(inputSize, 1024)
        self.fc2 = nn.Linear(1024, 768)
        self.fc3 = nn.Linear(768, 512) 
        self.fc4 = nn.Linear(512, 256)
        self.out = nn.Linear(256, outputSize)


    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = F.relu(self.fc4(x))
        x = self.out(x)
        return x
    
def trainNetwork(model, replayBuffer, batchSize, optimizer, gamma, device):
    if len(replayBuffer) < batchSize:
        return
    
    batch = replayBuffer.sample(batchSize)
    
    states, actions, nextStates, rewards, gameCompletions = zip(*batch)
    
    states = torch.tensor(states, dtype=torch.float32).to(device)
    actions = torch.tensor(actions, dtype=torch.long).unsqueeze(-1).to(device)
    nextStates = torch.tensor(nextStates, dtype=torch.float32).to(device)
    rewards = torch.tensor(rewards, dtype=torch.float32).to(device)
    gameCompletions = torch.tensor(gameCompletions, dtype=torch.bool).to(device)

    currentQ = model(states).gather(1, actions).squeeze(-1)
    
    nextQ = model(nextStates).detach().max(1)[0]
    nextQ[gameCompletions] = 0

    targetQ = rewards + (gamma * nextQ)

    loss = F.mse_loss(currentQ, targetQ)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    return loss.item()

def startTraining(model, replayBuffer, batchSize, inputSize, outputSize, gamma, trainingIterations):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = DQN(inputSize= inputSize, outputSize=outputSize).to(device)
    optimizer = optim.Adam(model.parameters(), lr=0.01)

    modelLosses = []

    for i in range(trainingIterations):
        loss = trainNetwork(model, replayBuffer, batchSize, optimizer, gamma, device)
        modelLosses.append(loss)    

    return model, modelLosses

