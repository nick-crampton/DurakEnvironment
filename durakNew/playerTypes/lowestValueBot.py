
from durakNew.player import Player
from durakNew.card import Card

class LowestValueBot(Player):
    def __init__(self, hand, playerID, gamestate):
        super().__init__(hand, playerID, gamestate)

    def chooseAction(self, possibleMoves, role = None):
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

            if len(attackDefensePairs) > 0:
                sortTuples = sorted(attackDefensePairs, key=lambda pair: (pair[0].getCardPower(), pair[1].getCardPower()))
                action = sortTuples[0]
                return action

            else:
                action = -1
                return action

        else:
            ##Get card actions:
            cardActions = [action for action in possibleMoves if isinstance(action, Card)]
            
            if len(cardActions) > 0:
                sortAttacks = sorted(cardActions, key = lambda card: (card.getCardPower()))
                action = sortAttacks[0]
            
            else:
                action = -1
                
            return action