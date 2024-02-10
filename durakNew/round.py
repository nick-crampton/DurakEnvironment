from durakNew.player import Player
from durakNew.deck import Deck
from durakNew.gamestate import GameState

from durakNew.utils.role import role
from durakNew.utils.printCardLists import printCardLists

class Round:
    def __init__(self, playerList, attackingPlayerIndex, gamestate):
        self.playerList = playerList
        self.attackingPlayerIndex = attackingPlayerIndex
        self.gamestate = gamestate

        ##Counter that tracks how many attackers pass on their go
        self.skipAttackCount = 0

    def determineRoles(self):
        numPlayers = len(self.playerList)

        for i in range(numPlayers):
            position = (self.attackingPlayerIndex + i) % numPlayers

            if position == 0:
                role = "Attacker"

            elif position == 1:
                role = "Defender"

            elif position == 2 and numPlayers >= 3:
                role = "Neighbour"
            
            else:
                role = "Bystander"

            self.playerList[i].setRole(role)

    def getUndefendedCards(self):
        undefendedCards = []       
        
        pileDifference = len(self.gamestate.attackingCards) - len(self.gamestate.defendingCards)

        if pileDifference == 0:
            return undefendedCards

        for i in range(0, len(self.gamestate.attackingCards)):
            if i >= len(self.gamestate.defendingCards):
                undefendedCards.append(self.gamestate.attackingCards[i]) 

        return undefendedCards       

    def possibleMoves(self, activePlayer):
        roleVal = role[activePlayer.getRole()]
        hand = activePlayer.getHand()

        ##Attacker
        if roleVal == 0:
            return hand
        
        ##Defender
        elif roleVal == 1:
            undefendedCards = self.getUndefendedCards()
            defensibleCards = []

            if len(undefendedCards) == 0:
                defensibleCards.append(0)
                return defensibleCards

            if len(undefendedCards) != 0:
                cardToDefend = undefendedCards[0]

                for card in hand:

                    if card.suit == self.gamestate.trumpSuit and cardToDefend.suit != self.gamestate.trumpSuit:
                        defensibleCards.append(card)

                    elif card.suit == cardToDefend.suit and card.getCardPower() > cardToDefend.getCardPower():
                        defensibleCards.append(card)

                if len(defensibleCards) == 0:
                    return []

            defensibleCards.append(-1)
            return defensibleCards
                        
        ##Neighbour
        elif roleVal == 2:
            if len(self.attackingCards) >= 6:
                return []
            
            ranksToAttack = []
            legibleAttacks = []

            for card in self.gamestate.defendingCards:
                r = card.getRank()

                if r not in ranksToAttack:
                    ranksToAttack.append(r)
            
            for card in self.gamestate.attackingCards:
                r = card.getRank()

                if r not in ranksToAttack:
                    ranksToAttack.append(r)

            for card in hand:
                r = card.getRank()

                if r in ranksToAttack:
                    legibleAttacks.append[card]

            legibleAttacks.append(0)
            return legibleAttacks

        ##Bystander
        else:
            return []

    def defenderPickup(self, activePlayer):
        
        print("Round is over. Defender picks up:")
        print(printCardLists(self.gamestate.attackingCards))

        activePlayer.addCards(self.gamestate.attackingCards)
        activePlayer.addCards(self.gamestate.defendingCards)

        self.gamestate.attackingCards.clear()
        self.gamestate.defendingCards.clear()

    def defenseCheck(self, defender, skipAttackCheck):
        totalAttacks = len(self.gamestate.attackingCards)

        ##Scenario 1: Defender has beaten all attacks thus far, and no attackers/neighbours
        ##Are able, or willing to attack

        ##Scenario 2: Attack has played 6 cards, and defender has defender beat all 6
        
        ##Scenario 3: Defender manages to defend with every card in their hand
        if len(defender.getHand()) == 0:
            return True

    def attackerTurn(self, attacker):
        pm = self.possibleMoves(attacker)
        action = attacker.chooseAction(pm, attacker.getRole())

        if action != 0:
            return action

    def defenderTurn(self, defender):
        pm = self.possibleMoves(defender)
        action = defender.chooseAction(pm, defender.getRole())

        ##Option 1: They opt to pickup all the cards in the defending pile
        if action == -1:
            return -1

        ##Option 2: The successfully defend the attack
        else:
            return action
    
    def talonDraw(self):
        playerIndex = self.attackingPlayerIndex

        for i in range(len(self.playerList)):
            currentPlayer = self.playerList[playerIndex]

            while (len(currentPlayer.getHand()) < 6) and (len(self.gamestate.talon) > 0):
                card = self.gamestate.talon.pop()
                currentPlayer.addCard(card)

            if (len(self.gamestate.talon) == 0):
                print("Talon has been emptied, drawing cards is over")

            playerIndex = (playerIndex - 1) % len(self.playerList)

    def playRound(self):
        iteration = 0
        actionList = []

        ##Assign roles to every player
        rolesDict = self.determineRoles()

        for player in self.playerList:
            print(player)

        ##Boolean that becomes true when the round is over
        isOver = False

        while not isOver:

            print(f"Iteration {iteration}:")

            ##Turn 0, only the attacker can do anything in the initial round
            if iteration == 0:
                attacker = self.playerList[self.attackingPlayerIndex]
                
                action = self.attackerTurn(attacker)
                actionList.append([action, 0])

                attacker.setRole(2)

            ##Turn 1, the defender responds to the action of t0
            elif iteration == 1:
                defenderIndex = (self.attackingPlayerIndex + 1) % len(self.playerList)
                defender = self.playerList[defenderIndex]

                action = self.defenderTurn(defender)

                ##If defender picks up, game is over.

                if action != -1:
                    actionList.append([action, 1])

                else:
                    isOver = True
                    self.defenderPickup(defender)
                    break

            ##For all turns after, every player is offered the turn to play
            else:
                for player in self.playerList: 
                    
                    if player.getRole() == "Attacker":
                        print("Attacker should not appear in this for loop! debug time")

                    elif player.getRole() == "Defender":
                        action = self.defenderTurn(player)

                        if action != -1:
                            actionList.append([action, 1])

                        else:
                            isOver = True
                            self.defenderPickup(player)
                            break
                
                    elif player.getRole() == "Neighbour":
                        action = self.attackerTurn(player)
                        
                        if action != 0:
                            actionList.append([action, 0])

            attackFlag = False

            for i in actionList:
                card = i[0]
                
                if i[1] == 0:
                    self.gamestate.attackingCards.append(card)
                    print(f"The {card} has been added to the attack pile.\n")
                    attackFlag = True

                if i[1] == 1 and attackFlag == False:
                    self.gamestate.defendingCards.append(card)
                    cardPos = len(self.gamestate.defendingCards) - 1
                    
                    attackCard = self.gamestate.attackingCards[cardPos]

                    print(f"The {card} has been used to defend {attackCard}\n")

            actionList.clear()

            iteration += 1

        ##Round is over
        
        ##Need to clear attack/defend piles

        ##Deal hands to players
        self.talonDraw()

        remainingPlayers = []

        ##If anyone's hand is still empty after talon draw, they are finished and out of the game
        for player in self.playerList:

            if len(player.hand) > 0:
                remainingPlayers.append(player)

            else:
                print(f"{player} bows out by clearing their hand")

        return remainingPlayers