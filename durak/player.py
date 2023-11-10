from enum import Enum

class playerRole(Enum):
    ATTACKER = 0
    DEFENDER = 1
    NEIGHBOUR = 2
    BYSTANDER = 3

class DurakPlayer:
    
    def __init__(self, playerID, npRandom, role: playerRole):
        self.npRandom = npRandom
        self.playerID = playerID
        self.hand = []
        self.role = role

        self.playCard()
        self.drawCard()
        self.attack()
        self.defend()
        self.passTurn()
        self.pickupCards()
