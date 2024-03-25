import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import random
from durakNew.playerTypes.DQN import agentDQN
from durakNew.playerTypes.DQN import replayBuffer


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
    
def trainNetwork(model, replayBuffer, batchSize, optimizer, gamma):
    if len(replayBuffer) < batchSize:
        return
    
    batch = random.sample(replayBuffer, batchSize)
    
    states, actions, nextStates, rewards, gameCompletion = zip(*batch)

    states = torch.tensor(states, dtype=torch.float32)
    actions = torch.tensor(actions, dtype=torch.long)
    nextStates = torch.tensor(nextStates, dtype=torch.float32)
    rewards = torch.tensor(rewards, dtype=torch.float32)
    gameCompletions = torch.tensor(gameCompletions, dtype=torch.float32)

    outputTensor = model(states)
    actionSelected = actions.unsqueeze(-1)
    currentQ = outputTensor.gather(1, actionSelected).squeeze(-1)
    
    nextQ = model(nextStates).detach().max(1)[0]

    targetQ = rewards + (gamma * nextQ * (1 - gameCompletions))

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
        loss = trainNetwork(model, replayBuffer, batchSize, optimizer, gamma)
        modelLosses.append(loss)    

    return model, modelLosses

