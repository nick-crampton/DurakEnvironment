from durakNew.player import Player
from durakNew.card import Card
from durakNew.utils.printCardLists import printCardLists
from durakNew.utils.roleDict import roleDict

class HumanPlayer(Player):
    def __init__(self, hand, playerID, gamestate):
        super().__init__(hand, playerID, gamestate)

    def chooseAction(self, possibleMoves, role):
        roleName = roleDict[role]

        if role == 0 or role == 2:

            print("You are attacking.\n")
            self.displayPossibleMoves(possibleMoves)

            ##Choose which card to attack with:
            while True:
                choice = input("Select your move (enter move number) or view game info (t/a/d/h): ")
                choice = choice.lower()

                if choice in ['t', 'a', 'd', 'h']:
                    self.printGamestate(choice)
                    continue

                try:
                    choice = int(choice)

                    if 0 <= choice < len(possibleMoves):
                        return possibleMoves[choice]
                    
                    else:
                        print("Card choice out of range. Select a number associated with a card")

                except ValueError:
                    print("Invalid Input, enter an applicable number or a command (t/a/d/h)")

        if role == 1:

            print("You are defending - All cards need to be defended.\n")

            undefendedCards = self.gamestate.undefendedCards()

            ##Choose which card to defend
            while True: 
                
                for i, card in enumerate(undefendedCards):
                    print(f"{i}>> Defend {card}")

                choice1 = input("Select which card to defend or view game info (t/a/d/h): ")
                choice1 = choice1.lower()

                if choice1 in ['t', 'a', 'd', 'h']:
                    self.printGamestate(choice1)
                    continue

                try:
                    choice1 = int(choice1)

                    if 0 <= choice1 < len(undefendedCards):
                        selectedAttackCard = undefendedCards[choice1]
                        defensibleActions = possibleMoves[choice1]

                        defensibleActions.append(-2)

                        ##Now choose a card to defend that card
                        print(f"Defending against the {selectedAttackCard}.")
                        self.displayPossibleMoves(defensibleActions)

                        while True:
                            choice2 = input("Select your move (enter move number) or view game info (t/a/d/h): ")
                            print()
                            choice2 = choice2.lower()

                            if choice2 in ['t', 'a', 'd', 'h']:
                                self.printGamestate(choice2)
                                continue

                            try:
                                choice2 = int(choice2)

                                if choice2 < (len(defensibleActions) - 2):
                                    defensiveCard = defensibleActions[choice2]
                                    return (defensiveCard, selectedAttackCard)
                                
                                elif choice2 == (len(defensibleActions) - 2):
                                    return -1
                                
                                elif choice2 == (len(defensibleActions) - 1):
                                    defensibleActions.pop()
                                    break

                                else:
                                    print("Card choice out of range. Select a number associated with a card")
                                
                            except ValueError:
                                print("Invalid Input, enter an applicable number or a command (t/a/d/h)")

    
                    else:
                        print("Card choice out of range. Select a number associated with a card")

                except ValueError:
                    print("Invalid Input, enter an applicable number or a command (t/a/d/h)")

    def displayPossibleMoves(self, possibleMoves):
        print("\nPossible Moves:  ")

        for i, move in enumerate(possibleMoves):

            if isinstance(move, Card):
                print(f"{i}>>  Play {move}")
            
            elif move == -1 and self.role == 1:
                print(f"{i}>>  Pickup cards")

            elif move == -1 and (self.role == 0 or self.role == 2):
                print(f"{i}>>  Pass on attacking")

            elif move == -2:
                print(f"{i}>>  Back")
    
    def printGamestate(self, letter):
        if letter == 't':
            print(f"Trump Suit: {self.gamestate.trumpSuit}")
        
        elif letter == 'a':
            print(f"Attacking pile: ")
            print(printCardLists(self.gamestate.getAttackCards()))

        elif letter == 'd':
            print(f"Defending Pile: ")
            print(printCardLists(self.gamestate.getDefenseCards()))

        elif letter == 'h':
            print(f"Hand: ")
            print(printCardLists(self.hand))