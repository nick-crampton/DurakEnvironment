from durakNew.player import Player
from durakNew.playerTypes.agent import Agent

from durakNew.deck import Deck
from durakNew.gamestate import GameState

from durakNew.utils.roleDict import roleDict
from durakNew.utils.printCardLists import printCardLists

class Round:
    def __init__(self, playerList, attackingPlayerID, gamestate):
        self.playerList = playerList
        self.attackingPlayerID = attackingPlayerID
        self.gamestate = gamestate

    def getNextID(self, id):
        
        for i, player in enumerate(self.playerList):
            
            ##Returns the first ID that is larger than parameter ID
            playerID = player.getID()
            if playerID > id:
                return playerID
                
            
        ##If none are larger, return the smallest ID (wraps round)
        playerID = self.playerList[0].getID()
        return playerID

            
    def getPlayerByID(self, id):
        for player in self.playerList:
            if player.getID() == id:
                return player

    def determineRoles(self):
        numPlayers = len(self.playerList)
        
        ##Set all players initially to bystanders
        for player in self.playerList:
            player.setRole(2)
        
        ##Assign attacker role
        attacker = self.getPlayerByID(self.attackingPlayerID)
        attacker.setRole(0)

        ##Assign defender
        defenderID = self.getNextID(self.attackingPlayerID)
        defender = self.getPlayerByID(defenderID)
        defender.setRole(1)

        for player in self.playerList:
            if player.getRole() == 2:
               print("Ping!!!")

        ##Assign other attacker if more than 2 players
        if numPlayers > 2:
            otherAttackerID = self.getNextID(defenderID)
            otherAttacker = self.getPlayerByID(otherAttackerID)
            otherAttacker.setRole(0)

    def possibleMoves(self, activePlayer, iteration = None):
        role = activePlayer.getRole()
        hand = activePlayer.getHand()

        ##Attacker
        if role == 0:
            if iteration > 0:
                
                if len(self.gamestate.getAttackCards()) > 0:
                    ranksOnTable = {card.rank for attackCard, defenseCard in self.gamestate.attackDefensePairs for card in (attackCard, defenseCard) if card}
                    legibleAttacks = [card for card in hand if card.rank in ranksOnTable]
                    legibleAttacks.append(-1)
                    return legibleAttacks
                
                hand.append(-1)
            
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
                        
        ##Bystander
        else:
            return []

    def defenderPickup(self, activePlayer, avgHandBefore = None):
        if self.gamestate.printGameplay:
            print("Defender picks up all cards on the table.")

        activePlayer.addCards(self.gamestate.getAttackCards())
        activePlayer.addCards(self.gamestate.getDefenseCards())

        if isinstance(activePlayer, Agent):
            avgHandAfter = activePlayer.averageHand()
            activePlayer.ingameReward(avgHandBefore, avgHandAfter)

        self.gamestate.attackDefensePairs.clear()

    def defenseCheck(self, defender, skipAttackCount):
        numAttackers = self.numAttackers()

        beatCheck = all(defense is not None for attack, defense in self.gamestate.attackDefensePairs)

        if beatCheck: 
           ##Scenario 1: Defender has beaten all attacks thus far, and no attackers/neighbours are able, or willing to attack.
            if skipAttackCount >= numAttackers:
                return True
            
            ##Scenario 2: Attack has played cards, and defender has defender beat all in initialHand
            elif len(self.gamestate.attackDefensePairs) == self.gamestate.initialHand:
                return True
        
        ##Scenario 3: Defender manages to defend with every card in their hand
        else:
            if (len(defender.hand) == 0) and (len(self.gamestate.getDefenseCards) >= 1):
                return True

    def attackerTurn(self, attacker, iteration):
        pm = self.possibleMoves(attacker, iteration)
        
        if isinstance(attacker, Agent):
            action = attacker.chooseAction(pm, attacker.getRole(), self.playerList)

        else:
            action = attacker.chooseAction(pm, attacker.getRole())
        
        return action

    def defenderTurn(self, defender):
        pm = self.possibleMoves(defender)
        
        if isinstance(defender, Agent):
            action = defender.chooseAction(pm, defender.getRole(), self.playerList)

        else:
            action = defender.chooseAction(pm, defender.getRole())
        
        return action
    
    def addAttack(self, card):
        self.gamestate.attackDefensePairs.append((card, None))

    def addDefense(self, defenseCard, attackCard):
        for i, (a, d) in enumerate(self.gamestate.attackDefensePairs):
            if a == attackCard and d is None:
                self.gamestate.attackDefensePairs[i] = (a, defenseCard)
                return True
        
        return False 

    def talonDraw(self, attackerIndex):
        order = [(attackerIndex + i) % len(self.playerList) for i in range(len(self.playerList))]

        for playerIndex in order:

            player = self.playerList[playerIndex]
            drawCount = 0

            while len(player.hand) < self.gamestate.initialHand and (len(self.gamestate.talon) > 0):
                card = self.gamestate.talon.pop()
                player.addCard(card)
                drawCount += 1

                if len(self.gamestate.talon) == 0:
                    if self.gamestate.printGameplay:
                        print("\nThe talon has been emptied.")
                    break

            if drawCount == 0:
                if self.gamestate.printGameplay:
                    print(f"Player {player.playerID} draws no cards")

            elif drawCount == 1:    
                if self.gamestate.printGameplay:
                    print(f"Player {player.playerID} draws a card")

            else:
                if self.gamestate.printGameplay:
                    print(f"Player {player.playerID} draws {drawCount} cards")
 
    def numAttackers(self):
        if len(self.playerList) > 2:
            return 2
        
        else:
            return 1

    def discardCards(self):
        for attack, defense in self.gamestate.attackDefensePairs:
            self.gamestate.discardPile.append(attack)
            if defense is not None:
                self.gamestate.discardPile.append(defense)

        self.gamestate.attackDefensePairs.clear()

    def playRound(self):
        iteration = 0

        self.determineRoles()
        numAttackers = self.numAttackers()

        if self.gamestate.printGameplay:
            for player in self.playerList:
                print(player)

        ##Boolean that becomes true when the round is over
        isOver = False

        ##Boolean that determines whether attacker/defenders won
        defenseSuccess = True

        while not isOver:

            if self.gamestate.printGameplay:
                print(f"\nIteration {iteration + 1}:")

            if iteration % 2 == 0:
                skipAttackCount = 0
                
                ##Turn 0, only the attacker can do anything in the initial round
                if iteration == 0:
                    attacker = self.getPlayerByID(self.attackingPlayerID)
                    
                    action = self.attackerTurn(attacker, iteration)
                    if self.gamestate.printGameplay:
                        print(f"Player {attacker.playerID} has played the {action} to begin the attack!")

                    self.addAttack(action)
                    
                    ##For agents, calculate average hand before and after playing an action, for rewards
                    if isinstance(attacker, Agent):
                        avgHandBefore = attacker.averageHand()

                    attacker.playCard(action)

                    if isinstance(attacker, Agent):
                        avgHandAfter = attacker.averageHand()
                        attacker.ingameReward(avgHandBefore, avgHandAfter)

                else:

                    for player in self.playerList:
                        
                        ##If player is the attacker or the bystander.
                        if player.getRole() == 0:
                            
                            if len(player.hand) == 0:
                                if self.gamestate.printGameplay:
                                    print(f"\nPlayer {player.playerID} has no more cards to attack with.")

                            ##Maximum of initialHand attack cards
                            if len(self.gamestate.attackDefensePairs) > (self.gamestate.initialHand - 1):
                                if self.gamestate.printGameplay:
                                    print("\nThere are now the maximum attack cards in play.")
                                break

                            action = self.attackerTurn(player, iteration)

                            ##For agents, calculate average hand before and after playing an action, for rewards
                            if isinstance(player, Agent):
                                avgHandBefore = player.averageHand()

                            if action != -1:

                                self.addAttack(action)
                                if self.gamestate.printGameplay:
                                    print(f"The {action} has been added to the attack pile.\n")
                                
                                player.playCard(action)
                                skipAttackCount = 0

                                if isinstance(player, Agent):
                                    avgHandAfter = player.averageHand()
                                    player.ingameReward(avgHandBefore, avgHandAfter)

                            else:
                                skipAttackCount += 1
                                if self.gamestate.printGameplay:
                                    print(f"Attacker does not contribute to attack.\n")

                                if isinstance(player, Agent):
                                    avgHandAfter = player.averageHand()
                                    player.ingameReward(avgHandBefore, avgHandAfter)

                                if self.defenseCheck(defender, skipAttackCount):
                                    isOver = True
                                    defenseSuccess = True
                                    break
                                
            else:
                defenderID = self.getNextID(self.attackingPlayerID)
                defender = self.getPlayerByID(defenderID)

                undefended = self.gamestate.undefendedCards()

                for _ in range(len(undefended)):

                    ##Return defenders action
                    action = self.defenderTurn(defender)

                    ##For agents, calculate average hand before and after playing an action, for rewards
                    if isinstance(defender, Agent):
                        avgHandBefore = defender.averageHand()

                    ##If action is -1, defender picks up all cards and round is over.
                    if action == -1:
                        if self.gamestate.printGameplay:
                            print(f"Round over, defender was unable to defend:\n{printCardLists(undefended)}\n")
                        isOver = True
                        defenseSuccess = False
                        break
                    
                    ##Else, play the card, check to see if defender has succeeded in defending all attacks.
                    else:
                        defenseCard, attackCard = action
                        
                        defenseCheck = self.addDefense(defenseCard, attackCard)
                        if self.gamestate.printGameplay:
                            print(f"The {attackCard} is defended by {defenseCard}\n")

                        if defenseCheck is False:
                            if self.gamestate.printGameplay:
                                print("\nFailed to defend attack. The attack card was not found.")
                            break

                        defender.playCard(defenseCard)

                        if isinstance(defender, Agent):
                            avgHandAfter = defender.averageHand()
                            defender.ingameReward(avgHandBefore, avgHandAfter)

                        if self.defenseCheck(defender, skipAttackCount):
                            isOver = True
                            defenseSuccess = True
                            break

            iteration += 1
        
        attackerIndex = None

        ##If defense is a success, all cards are sent to discard pile.
        if defenseSuccess is True:
            self.discardCards()
            
            if self.gamestate.printGameplay:
                print(f"End of round. Attack was beaten by defense.\nAll cards are moved to the discard pile.\n")

        ##If defense is unsuccessful, defender picks up all cards
        else:
            if isinstance(defender, Agent):
                self.defenderPickup(defender, avgHandBefore)

            else:
                self.defenderPickup(defender)
            
                
            if self.gamestate.printGameplay:
                print(f"End of round. Defender picks up all cards on the table.\n")

        self.talonDraw(self.attackingPlayerID)

        for i, player in enumerate(self.playerList):
            finishedPlayers = []
        
            if len(player.hand) == 0:
                
                if self.gamestate.printGameplay:
                    print(f"Player {player.playerID} has emptied their hand.\nThey bow out.")
                self.playerList.pop(i)

                finishedPlayers.append(player)

        if defenseSuccess is True:
            attackerID = self.getNextID(self.attackingPlayerID)

        else:
            attackerID = self.getNextID(self.getNextID(self.attackingPlayerID))

        return self.playerList, finishedPlayers, attackerID
        
        