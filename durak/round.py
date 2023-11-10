from enum import Enum
from player import playerPosition, DurakPlayer

import numpy as np

class attackerAction(Enum):
    ATTACK = 0
    PASS = 1

class defenderAction(Enum):
    DEFEND = 0
    PICK_UP = 1


class DurakRound:
    ###A round of Durak

    def __init__(self, playerList, trumpSuit, attacker, talon, npRandom):
        ''' Arguments:
            playerList: A list of the players
            TrumpSuit (Suit)
            Attacker (int): returns id of the attacker
            deck (deck): returns the talon '''
        
        self.playerList = playerList
        self.trumpSuit = trumpSuit
        self.attacker = attacker
        self.defender = (attacker + 1) % len (playerList)
        self.talon = talon
        self.npRandom = npRandom
        self.neighbours = self.determineNeighbours()
        self.pointer = attacker
        self.updatePlayerPositions()

    def updatePlayerPositions(self):
        playerListLength = len(self.playerList)


        for i in range(playerListLength):
            if i == self.attacker:
                self.playerList[i].position = playerPosition.ATTACKER
            
            elif i == self.defender:
                self.playerList[i].position = playerPosition.DEFENDER
            
            else:
                self.playerList[i].position = playerPosition.BYSTANDER

        if firstDefense is True:
            neighbour0, neighbour1 = self.determineNeighbours(defender)
            self.playerList[neighbour0].position = playerPosition.NEIGHBOUR
            self.playerList[neighbour1].position = playerPosition.NEIGHBOUR
           
    def firstDefense(self):
        self.firstDefense = True
        self.updatePlayerPositions()

    def determineNeighbours(self):
        neighbour0 = (self.defender - 1) % len(self.playerList)
        neighbour1 = (self.defender + 1) % len(self.playerList)

        return neighbour0, neighbour1

    def newRound(self):
        self.currentAttackCards = []
        self.successfulDefenseCards = []

        


