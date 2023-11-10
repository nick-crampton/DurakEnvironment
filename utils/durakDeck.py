from rlcard.games.base import Card

def durakDeck():
    ## Creates a standard durak deck of 36 cards
    suitList = ['S', 'H', 'D', 'C']
    rankList = ['6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    result = [Card(suit, rank) for suit in suitList for rank in rankList]
    return result
