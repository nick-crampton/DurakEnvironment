from durakNew.player import Player
from durakNew.card import Card
from durakNew.utils.rankList import rankList
from durakNew.utils.suitList import suitList 
import numpy as np
import random
import json
import os

class AgentPlayer(Player):
    def __init__(self, hand, playerID, gamestate, learningRate, discount, epsilon, deckCount):
        super().__init__(hand, playerID, gamestate)
        self.learningRate = learningRate
        self.discount = discount
        self.epsilon = epsilon
        self.deckCount = deckCount

        self.qTable = {}
        
        self.episode = []

        self.lastAction = None
        self.lastState = None
        self.lastReward = None

    def encodeCard(self, card):
        rankLow = ['6', '7', '8']
        rankMid = ['9', '10', 'J']
        rankHigh = ['Q', 'K', 'A']

        if card.rank in rankLow:
            encodedRank = 0
        
        elif card.rank in rankMid:
            encodedRank = 1

        elif card.rank in rankHigh:
            encodedRank = 2

        else:
            print("Not a card")
            return None

        if card.suit == self.gamestate.trumpSuit:
            encodedRank += 3

        return encodedRank

    def encodeActions(self, possibleMoves, state, encodingMapping = None):
        qValues = {}

        for action in possibleMoves:
            
            ##Encode the actions if they are a card
            if isinstance(action, Card):
                encodedAction = self.encodeCard(action)
            
            elif isinstance(action, tuple):
                encodedDefense = self.encodeCard(action[0])
                encodedAttack = self.encodeCard(action[1])
                encodedAction = (encodedDefense, encodedAttack)

            else:
                encodedAction = action

            ##Map the encodings to the action using a dict
            if encodingMapping is not None:
                encodingMapping[encodedAction] = action
            
            qValues[encodedAction] = self.qTable.get((state, encodedAction), 0)

        return qValues, encodingMapping

    def encodeAction(self, action):
        if isinstance(action, Card):
            encodedAction = self.encodeCard(action)
        
        elif isinstance(action, tuple):
            encodedDefense = self.encodeCard(action[0])
            encodedAttack = self.encodeCard(action[1])
            encodedAction = (encodedDefense, encodedAttack)

        else:
            encodedAction = action

        return encodedAction

    def receiveEndReward(self, reward):
        self.lastReward = reward

        self.updateQ(self.lastState, [])

    def qTableSelection(self, state, possibleMoves):
    
        encodingMapping = {}

        qValues, encodingMapping = self.encodeActions(possibleMoves, state, encodingMapping)

        maxQ = max(qValues.values())
        bestActions = [action for action, q in qValues.items() if q == maxQ]

        chosenAction = random.choice(bestActions)
        originalAction = encodingMapping[chosenAction]

        ##Returns 1) the original action to pass back into the game
        ## 2) Returns the encoded action
        return originalAction, chosenAction

    def updateQ(self, currentState, possibleMoves):
    
        lastState = self.lastState
        lastAction = self.lastAction

        reward = self.lastReward

        currentQ = self.qTable.get((lastState, lastAction), 0)

        nextQValues, _ = self.encodeActions(possibleMoves, currentState)
        maxNextQ = max(nextQValues) if nextQValues else 0

        self.qTable[(lastState, lastAction)] = currentQ + self.learningRate * (reward + self.discount * maxNextQ - currentQ)

    def chooseAction(self, possibleMoves, role, playerList):
        deckCount = self.deckCount
        currentState = tuple(self.getStateRepresentation(deckCount, playerList, role))

        if self.lastAction is not None and self.lastState is not None: 
            self.updateQ(currentState, possibleMoves)

        possibleMovesFlat = []
        ##Flatten possibleMoves if agent is defending
        if role == 1:
            
            undefended = self.gamestate.undefendedCards()
            attackDefensePairs = []

            for attackCard, defenses in zip(undefended, possibleMoves):

                for d in defenses:

                    if isinstance(d, Card):
                        attackDefensePairs.append((d, attackCard))

                    elif d == -1:
                        attackDefensePairs.append(-1)

            possibleMovesFlat = attackDefensePairs
        
        else:
            possibleMovesFlat = possibleMoves

        ##Choose action randomly
        if np.random.rand() < self.epsilon:
            originalAction = random.choice(possibleMovesFlat)
            qAction = self.encodeAction(originalAction)

        else:
            originalAction, qAction = self.qTableSelection(currentState, possibleMovesFlat)

        self.lastState = currentState
        self.lastAction = qAction

        return originalAction

    def encodeHand(self, deckCount):
        encodedHand = [0] * 6
        for card in self.hand:
            encodedRank = self.encodeCard(card)
            encodedHand[encodedRank] += 1

        return encodedHand

    def encodeHandLengths(self, deckCount, playerList):

        normalizeHandLength = [(len(player.getHand()) / deckCount) for player in playerList]

        return normalizeHandLength
    
    def encodeRole(self, role):

        roleEncoding = [0, 0, 0, 0]
        roleEncoding[role] = 1
        return roleEncoding

    def encodeTableCards(self, deckCount):

        attackVector = []
        defenseVector = []

        for attack, defense in self.gamestate.attackDefensePairs:
            
            encodeAttack = self.encodeCard(attack)
            attackVector.append(encodeAttack)

            if defense is not None:
                encodeDefense = self.encodeCard(defense)
            
            else:
                encodeDefense = 0

            defenseVector.append(encodeDefense)

        return attackVector, defenseVector

    def getStateRepresentation(self, deckCount, playerList, role):
        state = []
        state.extend(self.encodeHand(deckCount))
        state.extend(self.encodeHandLengths(deckCount, playerList))
        state.extend(self.encodeRole(role))
        
        attackVector, defenseVector = self.encodeTableCards(deckCount)
        state.extend(attackVector)
        state.extend(defenseVector)

        talonCount = len(self.gamestate.talon) / deckCount
        discardCount = len(self.gamestate.discardPile) / deckCount

        state.append(talonCount)
        state.append(discardCount)

        return state
    
    def averageHand(self):
        
        if not self.hand:
            return 0

        totalEncodedValue = sum(self.encodeCard(card) for card in self.hand)
        averageEncodedValue = totalEncodedValue / len(self.hand)

        return averageEncodedValue

    def ingameReward(self, before, after):
        avgDifference = after - before

        if avgDifference > 0:
            self.lastReward = 0.1

        elif avgDifference < 0:
            self.lastReward = -0.1

        else:
            self.lastReward = 0
