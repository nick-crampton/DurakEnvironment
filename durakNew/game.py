from durakNew.player import Player
from durakNew.round import Round
from durakNew.gamestate import GameState
from durakNew.playerTypes.humanPlayer import HumanPlayer
from durakNew.playerTypes.agent import Agent
from durakNew.deck import Deck

import random

class Game:
    def __init__(self, playerList, gameProperties):
        self.startPlayer = 0
        self.deck = None

        self.playerList = playerList
        self.gamestate = GameState()

        self.gameProperties = gameProperties
        self.gameLength = 0


    def setCardCount(self):
        cardCount = len(self.playerList) * self.gamestate.initialHand + self.gamestate.maxTalon
        self.gamestate.cardCount = cardCount

    def setInitialPlayers(self):
        playerCount = len(self.playerList)
        self.gamestate.initialPlayerCount = playerCount
        
    def dealHands(self, activeDeck, handCount = None, talonCount = None):
        initialHand = handCount if not None else 6
        
        for player in self.playerList:
            player.hand.clear()

        ##Deal cards to each player
        for i in range(0, initialHand):
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
            agent.durakCount += 1

        elif survivalCheck == True:
            reward = 1
            agent.survivalCount += 1

        agent.receiveEndReward(reward)

    def newGame(self):
        
        ##Generate and shuffle new deck
        self.deck = Deck.generateDeck()

        ##Deal cards to each player
        self.dealHands(self.deck, self.gameProperties['handCount'], self.gameProperties['talonCount'])

        self.gamestate.initialHand = self.gameProperties['handCount']
        self.gamestate.maxTalon = self.gameProperties['talonCount']

        ##Save to the game state A) The number of cards in play and B) The number of players at the start of the game
        self.setCardCount()
        self.setInitialPlayers()

        ##Toggle printing gameplay
        self.gamestate.printGameplay = self.gameProperties['printGameplay']

        ##Determine who starts
        attackingPlayerIndex = random.choice(self.playerList).getID()
        
        for player in self.playerList:
            player.gamestate = self.gamestate
        
        finishedAgentCount = 0
        agentCount = sum(1 for player in self.playerList if isinstance(player, Agent))
        
        finishedGamePlayers = []
        roundCounter = 1

        while len(self.playerList) > 1 and finishedAgentCount < agentCount:
            
            if self.gamestate.printGameplay:
                print(f"\n----------------------------\nRound {roundCounter}")

            round = Round(self.playerList, attackingPlayerIndex, self.gamestate)
            self.playerList, finishedPlayers, attackingPlayerIndex = round.playRound()

            self.gameLength += 1

            ##Check if Agent has finished
            if len(finishedPlayers) > 0:
                for player in finishedPlayers:
                    
                    ##If agent survives, end game prematurely...
                    if isinstance(player, Agent):
                        self.rewards(player, True)
                        finishedAgentCount += 1

                finishedGamePlayers.extend(finishedPlayers)       
            
            roundCounter += 1
        
        if self.gamestate.printGameplay:
            print(f"\nGAME OVER. {self.playerList[0]} is the Durak.")

        ##If agent is Durak, they will be last player in playerlist
        if isinstance(self.playerList[0], Agent) and self.playerList[0] not in finishedGamePlayers:
            self.rewards(self.playerList[0], False)
            finishedAgentCount += 1

            if self.gamestate.printGameplay:
                print("\nAgent is the Durak")

        ##Once game is finished, add all players back into playerList for next game...
        self.playerList.extend(finishedGamePlayers)

