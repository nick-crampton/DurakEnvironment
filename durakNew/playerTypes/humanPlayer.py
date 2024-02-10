from durakNew.player import Player
from durakNew.card import Card
from durakNew.utils.printCardLists import printCardLists

class HumanPlayer(Player):
    def __init__(self, hand, playerID, gamestate):
        super().__init__(hand, playerID, gamestate)

    def chooseAction(self, possibleMoves, role):
        self.displayPossibleMoves(possibleMoves)

        ##User is prompted to pick an action
        while True:
            choice = input("Select your move (enter move number) or view game info (t/a/d/h): ")
            print()
            choice = choice.lower()

            if choice in ['t', 'a', 'd', 'h']:
                self.printGamestate(choice)
                continue

            try:
                choice = int(choice)
                
                if 0 <= choice <= len(possibleMoves):
                    return possibleMoves[choice]
        
                else:
                    print("Card choice out of range. Select a number associated with a card")
                
            except ValueError:
                print("Invalid Input, enter an applicable number or a command (t/a/d/h)")
    
    def displayPossibleMoves(self, possibleMoves):
        print("\nPossible Moves:  ")

        for i, move in enumerate(possibleMoves):

            if isinstance(move, Card):
                print(f"{i}>>  Play {move}")
            
            elif move == -1:
                print(f"{i}>>  Pickup cards")

            elif move == 0:
                print(f"{i}>>  Pass on attacking")
    
    def printGamestate(self, letter):
        if letter == 't':
            print(f"Trump Suit: {self.gamestate.trumpSuit}")
        
        elif letter == 'a':
            print(f"Attacking pile: ")
            print(printCardLists(self.gamestate.attackingCards))

        elif letter == 'd':
            print(f"Defending Pile: ")
            print(printCardLists(self.gamestate.defendingCards))

        elif letter == 'h':
            print(f"Hand: ")
            print(printCardLists(self.hand))