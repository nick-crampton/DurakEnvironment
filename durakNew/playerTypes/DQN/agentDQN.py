from durakNew.player import Player
from durakNew.card import Card
from durakNew.utils.rankList import rankList
from durakNew.utils.suitList import suitList 
from durakNew.utils.suitList import getKeyFromValue
from durakNew.playerTypes.DQN import ReplayBuffer
import durakNew.playerTypes.DQN.training as Training
import numpy as np
import random
import torch

class AgentDQN(Player):
    def __init__(self, hand, playerID, gamestate, learningRate, discount, epsilon, gamma, model, replayBuffer):
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

        self.replayBuffer = replayBuffer
    
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
        if actionIndex == 0 or actionIndex == 1:
            return -1
        
        elif role == 0 and actionIndex <= 37:
            cardActionIndex = actionIndex - 2
             
            rankIndex = cardActionIndex % len(rankList)
            suitIndex = cardActionIndex // len(rankList)
            
            rankString = rankList[rankIndex][0]
            suitString = getKeyFromValue(suitList, suitIndex)
            
            return (suitString, rankString)
        
        elif role == 1:

            cardActionIndex = actionIndex - 38
            ##Determine attackCard Suit
            attackSuit = cardActionIndex // 117

            totalDefenses = 0
            
            for attackRank in range(len(rankList)):
                
                defensesForRank = (len(rankList) - 1 - attackRank) + len(rankList)

                if (totalDefenses + defensesForRank) > cardActionIndex:
                    defenseWithinRank = cardActionIndex - totalDefenses

                    if defenseWithinRank < (len(rankList) - 1 - attackRank)

                        defendSuit = attackSuit
                        defendRank = defenseWithinRank + 1 + attackRank

                    else:
                        defendSuit = self.gamestate.TrumpSuit
                        defendRank = defenseWithinRank - (len(rankList) - 1 - attackRank) 

                    attackSuitString = getKeyFromValue(suitList, attackSuit)
                    defendSuitString = getKeyFromValue(suitList, defendSuit)

                    attackRankString = rankList[attackRank][0]
                    defendRankString = rankList[defendRank][0]

                    attackCard = (attackSuitString, attackRankString)
                    defenseCard = (defendSuitString, defendRankString)

                    return (attackCard, defenseCard)

                totalDefenses += defensesForRank

        print("No action was found in the mapping")
        return None

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
            
            actionDecoded = self.dqnActionMapping(bestActionIndex, role)

            if actionDecoded == -1:
                action = -1

            else:

                for move in possibleMoves:

                    if role == 0:
                        suit = actionDecoded[0]
                        rank = actionDecoded[1]

                        if isinstance(move, Card):
                            cardSuit = move.getSuit()
                            cardRank = move.getRank()

                            if cardSuit == suit and cardRank == rank:
                                return move

                    elif role == 1:
                        defenseSuit = actionDecoded[0][0]
                        defenseRank = actionDecoded[0][1]

                        attackSuit = actionDecoded[1][0]
                        attackRank = actionDecoded[1][1]

                        if isinstance(move, tuple):
                            attackCard = move[0]
                            defenseCard = move[1]

                            if (defenseCard.getSuit() == defenseSuit and defenseCard.getRank() == defenseRank) and (attackCard.getSuit() == attackSuit and attackCard.getRank() == attackRank):
                                return move
                        
        self.replayBuffer.storeExperience(self.lastState, self.lastAction, currentState, self.lastReward)

        self.lastState = currentState
        self.lastAction = action

        return action





    