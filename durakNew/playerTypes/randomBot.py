import random
from durakNew.player import Player
from durakNew.card import Card

class RandomBot(Player):
    def __init__(self, hand, playerID, gamestate):
        super().__init__(hand, playerID, gamestate)

    def chooseAction(self, possibleMoves, role):
        if role == 1:

            ##Get a list of undefended cards
            undefended = self.gamestate.undefendedCards()

            ##Create all possible tuples of (defenseCard, attackCard) from possibleMoves nested lists
            attackDefensePairs = []

            ##Loop through nested lists, a list for each undefended card.
            for attackCard, defenses in zip(undefended, possibleMoves):
                ##loop through all cards that can defend said attack card
                for defenseCard in defenses:
                    
                    if isinstance(defenseCard, Card):
                        attackDefensePairs.append((defenseCard, attackCard))

                    if defenseCard == -1:
                        attackDefensePairs.append(-1)

            if len(attackDefensePairs) > 0:
                action = random.choice(attackDefensePairs)
                return action
        
        else:
            return random.choice(possibleMoves)