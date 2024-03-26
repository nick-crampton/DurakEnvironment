import random
class ReplayBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = []
        self.position = 0

    def storeExperience(self, currentState, action, nextState, reward, gameCompletion = False):
        if len(self.buffer) < self.capacity:
            self.append.buffer(None)
        
        self.buffer[self.position] = (currentState, action, nextState, reward, gameCompletion)
        self.position = (self.position + 1) % self.capacity

    def sample(self, batchSize):
        return random.sample(self.buffer, batchSize)
    
    def __len__(self):
        return len(self.buffer)
