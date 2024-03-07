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
        self.gameLength = 0

        self.agent = None


    def dealHands(self, activeDeck, handCount = None, talonCount = None):
        maxHand = handCount if not None else 6
        
        for player in self.playerList:
            player.hand.clear()

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

        if self.gamestate.printGameplay:
            print(f"Trump suit is {self.gamestate.trumpSuit}")

    def rewards(self, agent, survivalCheck):
        
        if survivalCheck == False:
            reward = -1
            self.durakCount += 1

        elif survivalCheck == True:
            reward = 1
            self.survivalCount += 1

        agent.receiveEndReward(reward)

        self.agent = agent

    def newGame(self):
        
        ##Generate and shuffle new deck
        self.deck = Deck.generateDeck(self.gameProperties['rankList'])

        ##Deal cards to each player
        self.dealHands(self.deck, self.gameProperties['handCount'], self.gameProperties['talonCount'])

        self.gamestate.maxHand = self.gameProperties['handCount']
        self.gamestate.maxTalon = self.gameProperties['talonCount']

        ##Toggle printing gameplay
        self.gamestate.printGameplay = self.gameProperties['printGameplay']

        ##Determine who starts
        attackingPlayerIndex = random.choice(self.playerList).getID()
        
        for player in self.playerList:
            player.gamestate = self.gamestate
        
        agentIn = True
        
        roundCounter = 1
        finishedGamePlayers = []

        while len(self.playerList) > 1 and agentIn:
            
            if self.gamestate.printGameplay:
                print(f"\n----------------------------\nRound {roundCounter}")

            round = Round(self.playerList, attackingPlayerIndex, self.gamestate)
            self.playerList, finishedPlayers, attackingPlayerIndex = round.playRound()

            self.gameLength += 1

            ##Check if Agent has finished
            if len(finishedPlayers) > 0:
                for player in finishedPlayers:
                    
                    ##If agent survives, end game prematurely...
                    if isinstance(player, AgentPlayer):
                        self.rewards(player, True)
                        
                        if self.gamestate.printGameplay:
                            print("\nAgent survives")
                        
                        agentIn = False
                        break

                finishedGamePlayers.extend(finishedPlayers)       
            
            roundCounter += 1
        
        if self.gamestate.printGameplay:
            print(f"\nGAME OVER. {self.playerList[0]} is the Durak.")

        ##If agent is Durak, they will be last player in playerlist
        if isinstance(self.playerList[0], AgentPlayer):
            self.rewards(self.playerList[0], False)
            
            if self.gamestate.printGameplay:
                print("\nAgent is the Durak")

        ##Once game is finished, add all players back into playerList for next game...
        self.playerList.extend(finishedGamePlayers)

