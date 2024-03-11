import torch
from durakNew.playerTypes.DQN import agentDQN

def convertToTensor(state):

    stateTensor = torch.tensor(state, dtype = torch.float)
    print(len(stateTensor))
    return stateTensor

