
from durakNew.player import Player

class LowestValueBot(Player):
    def __init__(self, hand, playerID):
        super().__init__(hand, playerID)

    def chooseAction(self, possibleMoves):
        pass