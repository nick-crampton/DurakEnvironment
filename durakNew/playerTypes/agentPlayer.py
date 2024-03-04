from durakNew.player import Player
from durakNew.card import Card
from durakNew.utils.rankList import rankList
from durakNew.utils.suitList import suitList 
import numpy as np
import random


class AgentPlayer(Player):
    def __init__(self, hand, playerID, gamestate, learningRate, discount, epsilon, qTable = None, isTraining = True):
        super().__init__(hand, playerID, gamestate)
        self.learningRate = learningRate
        self.discount = discount
        self.epsilon = epsilon

        self.qTable = qTable if qTable is not None else {}        
        self.stateActionCounter = {}
        
        self.episode = []

        self.lastAction = None
        self.lastState = None
        self.lastReward = None
        self.totalReward = 0

        self.isTraining = isTraining
        
    def encodeCard(self, card):
        rankLow = ['6', '7', '8']
        rankMid = ['9', '10', 'Jack']
        rankHigh = ['Queen', 'King', 'Ace']

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
                encodedAction = int(action)

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
        self.totalReward += reward

        self.updateQ(None, None, gameCompletion = True)

        self.lastState = None
        self.lastAction = None

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

    def updateQ(self, currentState, possibleMoves, gameCompletion = False):
        
        if not self.isTraining:
            return

        lastState = self.lastState
        lastAction = self.lastAction
        reward = self.lastReward

        ##Gets Q value of the last state and action used
        currentQ = self.qTable.get((lastState, lastAction), 0)

        ##If game is over, there is no next action
        if gameCompletion:
            maxNextQ = 0
        
        ##Gets the q values of all the possibleMoves, then gets the max qValue from these options
        else:
            nextQValues, _ = self.encodeActions(possibleMoves, currentState)
            maxNextQ = max(nextQValues.values()) if nextQValues else 0

        ##Q function which updates q value for state-action pair
        self.qTable[(lastState, lastAction)] = currentQ + self.learningRate * (reward + self.discount * maxNextQ - currentQ)

    def chooseAction(self, possibleMoves, role, playerList):
        currentState = tuple((key, value) for key, value in self.getStateRepresentation(playerList, role).items())
        print(currentState)


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

        ##Update the q table based on the PREVIOUS state-action pair
        if self.lastAction is not None and self.lastState is not None: 
            self.updateQ(currentState, possibleMovesFlat)

        ##Choose action randomly
        if np.random.rand() < self.epsilon:
            originalAction = random.choice(possibleMovesFlat)
            qAction = self.encodeAction(originalAction)

        else:
            originalAction, qAction = self.qTableSelection(currentState, possibleMovesFlat)

        stateActionPair = (currentState, qAction)

        if stateActionPair in self.stateActionCounter:
            self.stateActionCounter[stateActionPair] += 1
        
        else:
            self.stateActionCounter[stateActionPair] = 1

        self.lastState = currentState
        self.lastAction = qAction

        return originalAction

    def encodeHand(self):
        encodedHand = [0] * 6
        for card in self.hand:
            encodedRank = self.encodeCard(card)
            encodedHand[encodedRank] += 1

        return tuple(encodedHand)

    def encodeHandLengths(self, playerList):

        agentHandLen = len(self.hand)

        handLengthsEncoded = []

        for player in playerList:
            if player != self:

                if len(player.getHand()) > agentHandLen:
                    handLengthsEncoded.append(1)

                else:
                    handLengthsEncoded.append(0)
    
        return tuple(handLengthsEncoded)
    
    def encodeRole(self, role):

        roleEncoding = [0, 0]
        roleEncoding[role] = 1
        return tuple(roleEncoding)

    def encodeTableCards(self):

        attackVector = [0] * self.gamestate.maxHand
        defenseVector = [0] * self.gamestate.maxHand

        for i, (attack, defense) in enumerate(self.gamestate.attackDefensePairs):
            
            encodeAttack = self.encodeCard(attack)
            attackVector[i] = encodeAttack

            if defense is not None:
                encodeDefense = self.encodeCard(defense)
            
            else:
                encodeDefense = -1

            defenseVector[i] = encodeDefense

        return tuple(attackVector), tuple(defenseVector)

    def getStateRepresentation(self, playerList, role):
        state = {
            "hand": self.encodeHand(),
            "hand_lengths": self.encodeHandLengths(playerList),
            "role": self.encodeRole(role),
            "table_cards": self.encodeTableCards(),
            "talon": 1 if len(self.gamestate.talon) > 0 else 0
        }

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
            self.totalReward += 0.1

        elif avgDifference < 0:
            self.lastReward = -0.1
            self.totalReward -= 0.1

        else:
            self.lastReward = 0

