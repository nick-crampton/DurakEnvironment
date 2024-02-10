from durakNew.player import Player
from durakNew.round import Round
from durakNew.gamestate import GameState
from durakNew.playerTypes.humanPlayer import HumanPlayer
from durakNew.playerTypes.randomBot import RandomBot
from durakNew.deck import Deck

import random

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
        self.gamestate = GameState()

    def createPlayers(self, noPlayers):
        for i in range(noPlayers):
            
            playerType = self.playerTypes[i]

            if playerType == 0:
                ##Create HumanPlayer
                newPlayer = HumanPlayer([], i + 1, self.gamestate)
                pass
            elif playerType == 1:
                ##Create BotPlayer
                newPlayer = RandomBot([], i + 1,  self.gamestate)
                pass
            elif playerType == 2:
                ##Create AgentPlayer
                pass

            self.playerList.append(newPlayer)

    def dealHands(self, activeDeck):
        for _ in range(0, 6):
            for player in self.playerList:
                if not activeDeck.isEmpty():
                    card = activeDeck.drawCard()
                    player.addCard(card)

        card = activeDeck.drawCard()
        self.gamestate.trumpSuit = card.suit

    def newGame(self):
        ##First, create all the new players
        self.createPlayers(self.noPlayers)

        ##Generate and shuffle new deck
        self.deck = Deck.generateDeck()

        ##Deal 6 cards to each player
        self.dealHands(self.deck)

        ##Determine who starts
        attackingPlayerIndex = random.choice(self.playerList).getID()
        
        while len(self.playerList) > 1:
            round = Round(self.playerList, attackingPlayerIndex, self.gamestate)
            self.playerList = round.playRound()

        else:
            ##Losing Player
            lastPlayer = self.playerList[0]
            print(f"GAME OVER. {lastPlayer} is the Durak")



