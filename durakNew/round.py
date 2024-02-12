from durakNew.player import Player
from durakNew.deck import Deck
from durakNew.gamestate import GameState

from durakNew.utils.roleDict import roleDict
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
                role = 0

            elif position == 1:
                role = 1

            elif position == 2 and numPlayers >= 3:
                role = 2
            
            else:
                role = 3

            self.playerList[i].setRole(role)

    def possibleMoves(self, activePlayer):
        role = activePlayer.getRole()
        hand = activePlayer.getHand()

        ##Attacker
        if role == 0:
            return hand
        
        ##Defender
        elif role == 1:
            undefendedCards = self.gamestate.undefendedCards()
            defenses = []

            for attackCard in undefendedCards:
                
                defenseForAttack = []

                for card in hand:

                    if card.suit == self.gamestate.trumpSuit and attackCard.suit != self.gamestate.trumpSuit:
                        defenseForAttack.append(card)

                    elif card.suit == attackCard.suit and card.getCardPower() > attackCard.getCardPower():
                        defenseForAttack.append(card)

                defenseForAttack.append(-1)
                
                defenses.append(defenseForAttack)
            
            
            return defenses
                        
        ##Neighbour
        elif role == 2:
            if len(self.gamestate.attackingCards) >= 6:
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
                    legibleAttacks.append(card)

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
        return action

    def defenderTurn(self, defender):
        pm = self.possibleMoves(defender)
        action = defender.chooseAction(pm, defender.getRole())

        return action
    
    def addAttack(self, card):
        self.gamestate.attackDefensePairs.append((card, None))

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

            if iteration % 2 == 0:

                ##Turn 0, only the attacker can do anything in the initial round
                if iteration == 0:
                    attacker = self.playerList[self.attackingPlayerIndex]
                    
                    action = self.attackerTurn(attacker)

                    self.addAttack(action)
                    attacker.playCard(action)

                else:

                    for player in self.playerList:
                        
                        ##If player is the attacker or the bystander.
                        if player.getRole() == 0 or player.getRole() == 2:
                            
                            ##Maximum of 6 attack cards
                            if len(self.gamestate.attackDefensePairs) > 5:
                                print("There are now 6 attack cards in play.")
                                break

                            action = self.attackerTurn(player)

                            if action != 0:

                                self.addAttack(action)
                                print(f"The {action} has been added to the attack pile.")
                                
                                player.playCard(action)

            else:

                defenderIndex = (self.attackerPlayerIndex + 1) % len(self.playerList)
                defender = self.playerList[defenderIndex]

                undefended = self.gamestate.undefendedCards()

                for _ in range(len(undefended)):

                    action = self.defenderTurn(defender)

                    if action == -1:
                        isOver = True
                        break

                    else:
                        self.addDefense(action)
                        defender.playCard(action)

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