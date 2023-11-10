from copy import deepcopy
import numpy as np

from durak.dealer import Dealer

class DurakGame:
    def __init__(self, allowStepBack = False, numPlayers = 2):
        self.allowStepBack = allowStepBack
        self.npRandom = np.random.RandomState()
        self.numPlayers = numPlayers
        self.payoffs = [0 for _ in range(self.numPlayers)]

    def configure(self, gameConfig):
        self.numPlayers = gameConfig['gameNumPlayers']

    def initGame(self):
        self.payoffs = [0 for _ in range(self.numPlayers)]
        self.dealer = Dealer(self.npRandom)
        self.players = [Player(i, self.npRandom) for i in range(self.numPlayers)]

        for player in self.players:
            self.dealer.dealCards(player, 6)

        self.round = Round(self.players, self.dealer, self.numPlayers, self.npRandom)
        self.history = []

        playerID = self.round.currentPlayer
        state = self.getState(playerID)
        
        return state, playerID
    
    def step(self, action):
        if self.allowStepBack:
            hisDealer = deepcopy(self.dealer)
            hisRound = deepcopy(self.round)
            hisPlayer = deepcopy(self.players)
            self.history.append(hisDealer, hisPlayer, hisRound)

        self.round.proceedRound(self.players, action)
        playerID = self.round.currentPlayer
        state = self.getState(playerID)
        return state, playerID
    
    def stepBack(self):
        if not self.history:
            return False
        self.dealer, self.players, self.round = self.history.pop
        return True
    
    def getState(self, playerID):
        state = self.round.getState(self.players, playerID)
        state['numPlayers'] = self.getNumPlayers()
        state['currentPlayer'] = self.round.currentPlayer

        return state
    
    def getPayoffs(self):
        ### To implement!

        return self.playoffs
    
    def getLegalActions(self):
        return self.round.getLegalActions(self.players, self.round.currentPlayer)
    
    def getNumPlayers(self):
        return self.numPlayers

    @staticmethod

    def getNumActions():
        ##Placeholder
        
        return 61
    
    def getPlayerID(self):
        return self.round.currentPlayer
    
    def isOver(self):
        return self.round.isOver()
    


