from durakNew.player import Player
from durakNew.card import Card
from durakNew.utils.rankList import rankList
from durakNew.utils.suitList import suitList 
import numpy as np
import random

class AgentPlayer(Player):
    def __init__(self, hand, playerID, gamestate, learningRate, discount, epsilon, deckCount):
        super().__init__(hand, playerID, gamestate)
        self.qTable = qTable
        self.learningRate = learningRate
        self.discount = discount
        self.epsilon = epsilon
        self.deckCount = deckCount

        self.qTable = {}

    def chooseAction(self, possibleMoves, role, playerList, deckCount):

        state = tuple(self.getStateRepresentation(deckCount, playerList, role))
        
        if np.random.rand() < self.epsilon:
            randomAction = random.choice(possibleMoves)
            return randomAction

        else:
            qValues = {}

            for action in possibleMoves:
                qValues[action] = self.qTable.get((state, action), 0)

            maxQ = max(qValues.values())

            maxQ_Actions = [action for action, q in qValues.items() if q == maxQ]
            action = random.choice(maxQ_Actions)
            return action
    
    ##State representation
    def encodeHand(self, deckCount):
        encodedHand = [0] * deckCount
        for card in self.hand:
            rankIndex = dict(rankList)[card.rank]
            suitIndex = suitList[card.suit]

            cardIndex = (suitIndex * 9) + rankIndex
            encodedHand[cardIndex] = 1

        return encodedHand

    def encodeHandLengths(self, deckCount, playerList):

        normalizeHandLength = [(len(player.getHand()) / deckCount) for player in playerList]

        return normalizeHandLength
    
    def encodeRole(self, role):

        roleEncoding = [0, 0, 0, 0]
        roleEncoding[role] = 1
        return roleEncoding

    def encodeTrump(self):

        trumpEncoding = [0, 0, 0, 0]
        
        trumpIndex = suitList[self.gamestate.trumpSuit]
        trumpEncoding[trumpIndex] = 1

        return trumpEncoding
    
    def encodeTableCards(self, deckCount):

        tableEncoding = [0] * deckCount

        for card in self.gamestate.getAttackCards():
            
            cardIndex = (suitList[card.suit]) * 9 + dict(rankList)[card.rank]
            tableEncoding[cardIndex] = 1

        for card in self.gamestate.getDefenseCards():

            cardIndex = (suitList[card.suit]) * 9 + dict(rankList)[card.rank]
            tableEncoding[cardIndex] = 1

        return tableEncoding

    def getStateRepresentation(self, deckCount, playerList, role):
        state = []
        state.extend(self.encodeHand(deckCount))
        state.extend(self.encodeHandLengths(playerList))
        state.extend(self.encodeRole(role))
        state.extend(self.encodeTrump())
        state.extend(self.encodeTableCards(deckCount))

        talonCount = len(self.gamestate.talon) / deckCount
        discardCount = len(self.gamestate.discardPile) / deckCount

        state.append(talonCount)
        state.append(discardCount)

        return state
    
    def receiveReward(self, reward):
        