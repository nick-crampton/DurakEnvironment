from durakNew.player import Player
from durakNew.deck import Deck
from durakNew.gamestate import GameState

class Round:
    def __init__(self, playerList, attackingPlayerIndex, gamestate):
        self.playerList = playerList
        self.attackingPlayerIndex = attackingPlayerIndex
        self.gamestate = gamestate

    def determineRoles(self):
        numPlayers = len(self.playerList)

        for i in range(numPlayers):
            position = (self.attackingPlayerIndex + i) % numPlayers

            if position == 0:
                role = 0

            elif position == 1:
                role = 1

            elif position == 2 and numPlayers >= 3:
                role = 2
            
            else:
                role = 3

            self.playerList[i].setRole(role)

    def possibleMoves(self, activePlayer, attackingCard = None):
        p = activePlayer
        role = p.getRole()
        hand = p.getHand()

        ##Attacker
        if role == 0:
            return hand
        
        ##Defender
        elif role == 1:
            if attackingCard is None:
                raise ValueError("Attacking card is required")
            
            defenseCards = []

            aSuit = attackingCard.suit
            aRank = attackingCard.rank

            for card in self.hand:
                
                dSuit = card.suit
                dRank = card.rank

                if aSuit != self.gamestate.trumpSuit and dSuit == self.gamestate.trumpSuit:
                    defenseCards.append(card)

                elif dSuit == aSuit and (card.getCardPower() > attackingCard.getCardPower()):
                    defenseCards.append(card)

            return defenseCards

        ##Neighbour
        elif role == 2:
            if len(self.attackingCards) >= 6:
                return []
            
            ranksPlayed = {card.getRank() for card in (self.gamestate.attackingCards + self.gamestate.defendingCards)}
            return [card for card in hand if card.getRank() in ranksPlayed]
        
        ##Bystander
        else:
            return []

    def startRound(self):
        
        ##Assign roles to every player
        self.determineRoles()

        ##Boolean that becomes true when the round is over
        isOver = False

        ##Sets active player to be the attacker, who always starts
        activePlayerIndex = self.playerList.index(attackingPlayerIndex)
        activePlayer =  self.playerList[activePlayerIndex]

        pm = self.possibleMoves(activePlayer)
        action = activePlayer.chooseAction(pm)
        self.gamestate.attackingCard.append(action)

        ##Defender then defends
        activePlayer += 1
        pm = self.possibleMoves(activePlayer)
        action = activePlayer.chooseAction(pm)

        if action == -1:
            isOver = True
        
        while not isOver:
            

        else:
            self.gamestate.defendingCard.append(action)

        
            

            

