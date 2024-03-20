
class Agent(Player):
    def __init__(self, hand, playerID, gamestate, learningRate, discount, epsilon):
        super().__init__(hand, playerID, gamestate)
        self.learningRate = learningRate
        self.discount = discount
        self.epsilon = epsilon

        self.lastAction = None
        self.lastState = None
        self.lastReward = None
        self.totalReward = 0

    def averageHand(self):
            
        if not self.hand:
            return 0

        totalEncodedValue = sum(self.encodeCard(card) for card in self.hand)
        averageEncodedValue = totalEncodedValue / len(self.hand)

        return averageEncodedValue
    
    def ingameReward(self, before, after):
        avgDifference = after - before

        if avgDifference > 0:
            self.lastReward = 0.1
            self.totalReward += 0.1

        elif avgDifference < 0:
            self.lastReward = -0.1
            self.totalReward -= 0.1

        else:
            self.lastReward = 0

