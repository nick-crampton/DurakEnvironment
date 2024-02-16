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
        self.reward = None

    def receiveReward(self, reward):
        self.reward = reward

    def updateQValues(self):
        
        for state, action in reversed(self.episode):

            qValue = self.qTable.get((state, action), 0)
            ##Return the highest future Q-value based on the next state and all actions within an episode/game.
            bestQ = max((self.qTable.get(nextState, nextAction), 0) for nextState, nextAction in self.episode if nextState != state)

            ##Q-learning function
            qValue += self.learningRate * ((self.reward + self.discount) * bestQ - qValue)

            self.qTable[(state, action)] = qValue

    def chooseAction(self, possibleMoves, role, playerList):
        deckCount = self.deckCount

        currentState = tuple(self.getStateRepresentation(deckCount, playerList, role))

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

            encodedActions = [self.encodeAction(action) for action in attackDefensePairs]

            if np.random.rand() < self.epsilon:
                chosenAction = random.choice(encodedActions)
            
            else:
                qValues = {}

                for action in possibleMoves:
                    ##Gets actions from qTable given state if it exists
                    ##If not returns 0
                    qValues[action] = self.qTable.get((currentState, action), 0)

                ##Returns best possible action
                maxQ = max(qValues.values())

                maxQ_Actions = [action for action, q in qValues.items() if q == maxQ]
                chosenAction = random.choice(maxQ_Actions)

                self.episode.append((currentState, chosenAction))


        if np.random.rand() < self.epsilon:
            chosenAction = random.choice(possibleMoves)
            return chosenAction

        else:
            qValues = {}

            for action in possibleMoves:
                qValues[action] = self.qTable.get((currentState, action), 0)

            maxQ = max(qValues.values())

            maxQ_Actions = [action for action, q in qValues.items() if q == maxQ]
            chosenAction = random.choice(maxQ_Actions)

            self.episode.append((currentState, chosenAction))
            return chosenAction

    def encodeAction(self, action):
        if isinstance(action, tuple) and isinstance(action[0], Card):
            return ('defend', action[0].suit, action[0].rank, action[1].suit, action[1].rank)
        
        elif isinstance(action, Card):
            return ('action', action.suit, action.rank)
        
        elif isinstance(action, int):
            if action == -1:
                return ('pickup', -1)
            
            if action == 0:
                return ('skip', 0)
            
        return None

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
        state.extend(self.encodeHandLengths(deckCount, playerList))
        state.extend(self.encodeRole(role))
        state.extend(self.encodeTrump())
        state.extend(self.encodeTableCards(deckCount))

        talonCount = len(self.gamestate.talon) / deckCount
        discardCount = len(self.gamestate.discardPile) / deckCount

        state.append(talonCount)
        state.append(discardCount)

        return state
    

