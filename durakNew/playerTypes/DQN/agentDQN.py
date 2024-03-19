from durakNew.player import Player
from durakNew.card import Card
from durakNew.utils.rankList import rankList
from durakNew.utils.suitList import suitList 
import durakNew.playerTypes.DQN.training as Training
import numpy as np
import random
import torch

class AgentDQN(Player):
    def __init__(self, hand, playerID, gamestate, learningRate, discount, epsilon, gamma, model):
        super().__init__(hand, playerID, gamestate)
        self.learningRate = learningRate
        self.discount = discount
        self.epsilon = epsilon
        self.gamma = gamma

        self.lastAction = None
        self.lastState = None
        self.lastReward = None
        self.totalReward = 0

        self.model = model.to(Training.device)
        self.model.eval()
    
    def encodeCard(self, card):
        encodedCard = [0] * 13
        
        if isinstance(card, Card):
            (suitValue, rankValue) = card.getCardPower()
            
            encodedCard[rankValue] = 1
            encodedCard[9 + suitValue] = 1
        
        return encodedCard

    def encodeHand(self):
        maxHand = self.gamestate.cardCount - 1

        encodedHand = [[0] * 13 for i in range(maxHand)]

        for i, card in enumerate(self.hand):
            encodedCard = self.encodeCard(card)
            encodedHand[i] = encodedCard
        
        return encodedHand
        
    def encodeDiscardPile(self, discardPile):
        maxDiscardPile = self.gamestate.cardCount - 2

        encodedDiscardPile = [[0] * 13 for i in range(maxDiscardPile)]

        for i, card in enumerate(discardPile):
            encodedCard = self.encodeCard(card)
            encodedDiscardPile[i] = encodedCard

        return encodedDiscardPile
    
    def encodeTableCards(self):
        attackVector = [0] * self.gamestate.initialHand
        defenseVector = [0] * self.gamestate.initialHand

        attackVector = [[0] * 13 for i in range(self.gamestate.initialHand)]
        defenseVector = [[0] * 13 for i in range(self.gamestate.initialHand)]

        for i, (attack, defense) in enumerate(self.gamestate.attackDefensePairs):
            
            encodeAttack = self.encodeCard(attack)
            attackVector[i] = encodeAttack

            if defense is not None:
                encodeDefense = self.encodeCard(defense)
            
            else:
                encodeDefense = self.encodeCard(0)

            defenseVector[i] = encodeDefense

        return attackVector, defenseVector

    def encodeRole(self, role):
        roleEncoding = [0, 0]
        roleEncoding[role] = 1
        
        return tuple(roleEncoding)
    
    def encodeTalon(self):
        currentTalonLength = len(self.gamestate.talon)
        encodedTalon = currentTalonLength / self.gamestate.maxTalon

        return encodedTalon

    def encodeTrump(self, trump):
        trumpEncoding = [0] * 4
        trumpValue = suitList.get(trump)

        trumpEncoding[trumpValue] = 1

        return trumpEncoding
    
    def encodeHandLengths(self, playerList):
        handLengthEncoding = [0] * self.gamestate.initialPlayerCount

        for i, player in enumerate(playerList):
            handLength = len(player.hand)
            i = player.getID()

            handLengthEncoding[i] = handLength

        return handLengthEncoding
    
    def getStateRepresentation(self, playerList, role):
        state = []
        
        encHand = self.encodeHand()
        for card in encHand:
            state.extend(card)

        encDiscardPile = self.encodeDiscardPile(self.gamestate.discardPile)
        for card in encDiscardPile:
            state.extend(card)
        
        encAttackVector, encDefenseVector = self.encodeTableCards()
        for card in encAttackVector:
            state.extend(card)
        for card in encDefenseVector:
            state.extend(card)

        encHandLengths = self.encodeHandLengths(playerList)
        state.extend(encHandLengths)

        encRole = self.encodeRole(role)
        state.extend(encRole)

        encTalon = self.encodeTalon()
        state.append(encTalon)

        encTrump = self.encodeTrump(self.gamestate.trumpSuit)
        state.extend(encTrump)

        return state
    
    def dqnActionMapping(self, actionIndex, role):
        if actionIndex == 0:
            return -1
        
        elif actionIndex == 1:
            return -1
        
        elif role == 0 and actionIndex <= 37:
            cardActionIndex= actionIndex - 2
             
            rankIndex = cardActionIndex % len(rankList)
            suitIndex = cardActionIndex // len(rankList)
            return (rankIndex, suitIndex)
        
        elif role == 1:
            trumpSuit = self.gamestate.trumpSuit
            ##trumpValue =

            
            


    def chooseAction(self, possibleMoves, role, playerList):
        currentState = self.getStateRepresentation(playerList, role)
        stateTensor = Training.convertToTensor(currentState)

        with torch.no_grad():
            qValues = self.model(stateTensor)

        if np.random.rand() < self.epsilon:
            action = random.choice(possibleMoves)

        else:
            qValues = qValues.cpu().numpy().squeeze()
            actionIndices = [self.encodeAction(action, possibleMoves, role) for action in possibleMoves]
            validQ = qValues[actionIndices]
            bestActionIndex = np.argmax(validQ)
            action = possibleMoves[bestActionIndex]

        ##Store experience
            
        self.lastState = currentState
        self.lastAction = action

        return action





    