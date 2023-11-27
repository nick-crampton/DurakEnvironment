from durakNew.player import Player
from durakNew.deck import Deck
from durakNew.gamestate import GameState

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
        role = activePlayer.getRole()
        hand = activePlayer.getHand()

        ##Attacker
        if role == 0:
            return hand
        
        ##Defender
        elif role == 1:
            undefendedCards = self.getUndefendedCards()
            defensibleCards = []

            if len(undefendedCards) != 0:
                cardToDefend = undefendedCards[0]

                for card in hand:

                    if card.suit == self.gamestate.trumpSuit and cardToDefend.suit != self.gamestate.trumpSuit:
                        defensibleCards.append(card)

                    elif card.suit == cardToDefend.suit and card.getCardPower() > cardToDefend.getCardPower():
                        defensibleCards.append(card)

                if len(defensibleCards) == 0:
                    return []

                return defensibleCards
                        
        ##Neighbour
        elif role == 2:
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

            return legibleAttacks

        ##Bystander
        else:
            return []

    def defenderPickup(self, activePlayer):
        
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
        action = attacker.chooseAction(pm)

        if action != 0:
            return action

    def defenderTurn(self, defender):
        pm = self.possibleMoves(defender)
        action = defender.chooseAction(pm)

        ##Option 1: They opt to pickup all the cards in the defending pile
        if action == -1:
            self.defenderPickup(defender)
            return -1

        ##Option 2: The successfully defend the attack
        else:
            return action
    
    def playRound(self):
        iteration = 0
        actionList = []

        ##Assign roles to every player
        self.determineRoles()

        ##Boolean that becomes true when the round is over
        isOver = False

        while not isOver:

            print(f"Iteration {iteration}:\n")

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

                if action != 0:
                    actionList.append([action, 1])

                else:
                    isOver = True
                    break

            else:
                for player in self.playerList: 
                    
                    if player.getRole() == 0:
                        print("Attacker should not appear in this for loop! debug time")

                    elif player.getRole() == 1:
                        defender = self.playerList[player]
                        action = self.defenderTurn(defender)

                        if action != -1:
                            actionList.append([action, 1])

                        else:
                            isOver = True
                            break
                
                    elif player.getRole() == 2:
                        neighbour = self.playerList[player]
                        
                        action = self.attackerTurn(neighbour)
                        
                        if action != 0:
                            actionList.append([action, 0])

                attackFlag = False

                for i in actionList:
                    card = i[0]
                    
                    if i[1] == 0:
                        self.gamestate.attackingCards.append(card)
                        print(f"The {card} has been added to the attack pile.")
                        attackFlag = True

                    if i[1] == 1 and attackFlag == False:
                        self.gamestate.defendingCards.append(card)
                        cardPos = self.gamestate.defendingCards[-1]
                        
                        attackCard = self.gamestate.attackingCards[cardPos]

                        print(f"The {card} has been used to defend {attackCard}")

                iteration += 1
            

