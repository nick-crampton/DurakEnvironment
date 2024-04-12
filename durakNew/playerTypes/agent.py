from durakNew.player import Player

class Agent(Player):
    def __init__(self, hand, playerID, gamestate, lrParameters):
        super().__init__(hand, playerID, gamestate)

        self.lrParameters = lrParameters
        ##Contains learningRate, discount and epsilon

        self.learningRate = lrParameters['learningRate']
        self.discount = lrParameters['discount']
        
        self.epsilon = lrParameters['epsilon']
        self.epsilonValue = self.epsilon['value']
        self.decayType = self.epsilon['min']
        self.decayPortion = self.epsilon['decay']

        self.lastAction = None
        self.lastState = None
        self.lastReward = None
        self.totalReward = 0

        self.survivalCount = 0
        self.durakCount = 0

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

    def updateEpsilon(self, iterations):
        if self.decayType == "lin":
            linearDecay = 1.0 - 0.9 * (self.epsilonValue / (self.decayPortion * iterations))
            self.epsilonValue = linearDecay

        elif self.decayType == "exp":
            exponentialDecay = 1.0 * 0.1 ** (self.epsilonValue / (self.decayPortion * iterations))
            self.epsilonValue = exponentialDecay
