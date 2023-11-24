from durakNew.player import Player
from durakNew.card import Card

class HumanPlayer(Player):
    def __init__(self, hand, playerID, gameState):
        super().__init__(hand, playerID, gameState)

    def chooseAction(self, possibleMoves):
        self.displayPossibleMoves(possibleMoves)

        ##User is prompted to pick an action
        while True:
            choice = input("Select your move (enter move number) or view game info (t/a/d)")
            choice = choice.lower()

            if choice in ['t', 'a', 'd']:
                self.printGameState(choice)
                continue

            try:
                if 0 <= choice <= len(possibleMoves):
                    return possibleMoves[choice]
        
                else:
                    print("Card choice out of range. Select a number associated with a card")
                
            except ValueError:
                print("Invalid Input, enter an applicable number or a command (t/a/d)")
    
    def displayPossibleMoves(self, possibleMoves):
        print("\nPossible Moves:  ")

        for i, move in enumerate(possibleMoves):

            if isinstance(move, Card):
                print(f"{i}>>  Play {move}")
            
            elif move == -1:
                print(f"{i}>>  Pickup cards")

            elif move == 0:
                print(f"{i}>>  Pass on attacking")
    
    def printGameState(self, letter):
        if letter == 't':
            print(f"Trump Suit: {self.gameState.trumpSuit}")
        
        elif letter == 'a':
            print(f"Attacking Pile: {self.gameState.attackingCards}")

        elif letter == 'd':
            print(f"Defending Pile: {self.gameState.defendingCards}")

