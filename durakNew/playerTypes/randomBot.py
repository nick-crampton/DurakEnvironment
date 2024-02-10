import random
from durakNew.player import Player

class RandomBot(Player):
    def __init__(self, hand, playerID, gamestate):
        super().__init__(hand, playerID, gamestate)

    def chooseAction(self, possibleMoves):
        return random.choice(possibleMoves)