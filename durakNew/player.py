
from durakNew.card import Card
from durakNew.utils.rankList import rankList
from durakNew.utils.suitList import suitList
from durakNew.utils.roleDict import roleDict

class Player:
    def __init__(self, hand, playerID, gamestate):
        self.hand = hand
        self.playerID = playerID
        self.role = None
        self.gamestate = gamestate

    def getID(self):
        return self.playerID

    def getHand(self):
        return self.hand
    
    def getRole(self):
        return self.role
    
    def getActions(self, possibleMoves):

        actions = []

        for move in possibleMoves:
            
            if isinstance(move, Card):
                actionID = self.encodeCardAction(move)

            elif move == "pickupCards":
                actionID = -1

            elif move == "pass":
                actionID = 0

            else:
                actionID = None

            actions.append(actionID)

        return actions

    def encodeCardAction(self, card, trumpSuit):
        rankPower = dict(rankList)

        rankStrength = rankPower[card.rank]

        if card.suit == trumpSuit:
            rankStrength += 9
        
        return rankStrength

    def setRole(self, role):
        self.role = role
    
    def sortHand(self):
        self.hand.sort(key = lambda card: card.getCardPower())

    def addCard(self, card):
        self.hand.append(card)
        self.sortHand()

    def addCards(self, cards):
        self.hand.extend(cards)
        self.sortHand()

    def playCard(self, card):
        self.hand.remove(card)

    def __str__(self):
        handStr = ', '.join(str(card) for card in self.hand)
        roleName = roleDict.get(self.role)
        return (f"Player {self.playerID} - {roleName}\nHand: {handStr}\n")