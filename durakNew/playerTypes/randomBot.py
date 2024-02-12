import random
from durakNew.player import Player

class RandomBot(Player):
    def __init__(self, hand, playerID, gamestate):
        super().__init__(hand, playerID, gamestate)

    def chooseAction(self, possibleMoves, role = None):
        if role == 1:

            ##Create all possible tuples of (attackIndex, defenseCard) from possibleMoves nested lists
            attackDefensePairs = []

            ##Loop through nested lists, a list for each undefended card.
            for attackIndex, sublist in enumerate(possibleMoves):
                ##loop through all cards that can defend said attack card
                for dCard in sublist:
                    attackDefensePairs.append((attackIndex, dCard))


            if len(attackDefensePairs) > 0:
                action = random.choice(attackDefensePairs)
                attackIndex, card = action

                return card, attackIndex
        
        else:
            return random.choice(possibleMoves)