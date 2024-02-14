from durakNew.player import Player
import numpy as np

class AgentPlayer(Player):
    def __init__(self, hand, playerID, gamestate, qTable = None, learningRate = lr, discount = d, epsilon = e):
        super().__init__(hand, playerID, gamestate)
        self.qTable = qTable
        self.learningRate = learningRate
        self.discount = discount
        self.epsilon = epsilon

##State representation

##Agent's hand
##Encode each card as a combination of suit/rank - onehot encoding?

##Number of cards in each player's hand
##Vector where each element represents the number of cards held by each player, normalized by the maximum hand size to keep values between [0,1]

##Talon Count
##Normalized value indicating the fraction of the total deck remaining
        
##Discard pile count
##Normalized value representing the size of the discard pile relative to deck size.

##Attack Defense piles
##Encode cards similar to above.

##Current agent role
##encoded vector with bit for each possible role (attacker, defender, bystander)
        
##Trump Suit?
        
##Number of trump cards