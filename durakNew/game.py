from durakNew.player import Player
from durakNew.round import Round
from durakNew.gamestate import GameState
from durakNew.playerTypes.humanPlayer import HumanPlayer
from durakNew.playerTypes.randomBot import RandomBot
from durakNew.playerTypes.agentPlayer import AgentPlayer
from durakNew.deck import Deck

import random

class Game:
    def __init__(self, playerList, lrParams = None, gameProperties = None):
        self.startPlayer = 0
        self.deck = None

        self.playerList = playerList
        self.initialPlayers = playerList
        self.gamestate = GameState()

        self.lrParams = lrParams if not None else {}
        self.gameProperties = gameProperties if not None else {}

        ##Track Agent performance
        self.survivalCount = 0
        self.durakCount = 0
        self.totalReward = 0


    def dealHands(self, activeDeck, handCount = None, talonCount = None):
        maxHand = handCount if not None else 6
        
        ##Deal cards to each player
        for i in range(0, maxHand):
            for player in self.playerList:
                if not activeDeck.isEmpty():
                    card = activeDeck.drawCard()
                    player.addCard(card)

        self.gamestate.talon.extend(activeDeck.cards)
        
        if talonCount is not None:
            self.gamestate.talon = self.gamestate.talon[:talonCount]
        
        activeDeck.cards.clear()

        trumpCard = self.gamestate.talon[-1]
        self.gamestate.trumpSuit = trumpCard.suit

        print(f"Trump suit is {self.gamestate.trumpSuit}\n")

    def rewards(self):
        durak = self.playerList[0]

        print(f"\nGAME OVER. {durak} is the Durak.")

        for player in self.initialPlayers:
            if isinstance(player, AgentPlayer):
                if player == durak:
                    reward = -1
                    self.durakCount += 1

                else:
                    reward = 1
                    self.survivalCount += 1

                player.receiveReward(reward)
                self.totalReward += reward

    def newGame(self):
        
        ##Generate and shuffle new deck
        self.deck = Deck.generateDeck(self.gameProperties['rankList'])

        ##Deal cards to each player
        self.dealHands(self.deck, self.gameProperties['handCount'], self.gameProperties['talonCount'])

        self.gamestate.maxHand = self.gameProperties['handCount']
        self.gamestate.maxTalon = self.gameProperties['talonCount']

        ##Determine who starts
        attackingPlayerIndex = random.choice(self.playerList).getID()
        
        for player in self.playerList:
            player.gamestate = self.gamestate
        
        while len(self.playerList) > 1:
            round = Round(self.playerList, attackingPlayerIndex, self.gamestate)
            self.playerList, attackingPlayerIndex = round.playRound()

        self.rewards()

