from durakNew.player import Player
from durakNew.gamestate import GameState
from durakNew.playerTypes.humanPlayer import HumanPlayer
from durakNew.playerTypes.randomBot import RandomBot
from durakNew.deck import Deck

from random import random

playerType = {
    "Human": 0,
    "Bot": 1,
    "Agent": 2
}

class Game:
    def __init__(self, playerTypes):
        self.noPlayers = len(playerTypes)
        self.playerTypes = playerTypes

        self.startPlayer = 0
        self.deck = None

        self.playerList = []

    def createPlayers(self, noPlayers):
        for i in range(noPlayers):
            
            playerType = self.playerTypes[i]

            if playerType == 0:
                ##Create HumanPlayer
                newPlayer = HumanPlayer([], i)
                pass
            elif playerType == 1:
                ##Create BotPlayer
                newPlayer = RandomBot([[], i])
                pass
            elif playerType == 2:
                ##Create AgentPlayer
                pass

            newPlayer = Player([], i)
            self.playerList.append(newPlayer)

    def dealHands(self, activeDeck):
        for _ in range(0, 6):
            for player in self.playerList:
                if not activeDeck.isEmpty():
                    card = activeDeck.drawCard()
                    player.addCard(card)

    def newGame(self):
        ##First, create all the new players
        self.createPlayers(self.noPlayers)

        ##Generate and shuffle new deck
        self.deck = Deck.generateDeck()

        ##Deal 6 cards to each player
        self.dealHands(self.deck)

        for player in self.playerList:
            print(player)

        gamestate = GameState()
        
        ##Determine who starts
        attackingPlayer = random.choice(self.playerList)

        while not isOver:
            round = Round(self.playerList, attackingPlayer, gamestate)
            
            round.startRound()

            ##TO DO: Place checker that determines when game is over.


