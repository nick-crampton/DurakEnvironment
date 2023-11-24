import random
from durakNew.player import Player

class RandomBot(Player):
    def __init__(self, hand, playerID):
        super().__init__(hand, playerID)

    def chooseAction(self, possibleMoves):
        return random.choice(possibleMoves)