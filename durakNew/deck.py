import numpy as np
from durakNew.card import Card

from durakNew.utils.rankList import rankList
from durakNew.utils.suitList import suitList

def setTrumpSuit(card):
    
    ##Resets trumpSuit from previous game
    for suit in suitList:
        suitList[suit] = 0

    ##When given a card from the deck, the suit of that card determines the trump suit for the game
    suitList[card.suit] = 1

class Deck:
    def __init__(self, cards):
        self.cards = cards

    def drawCard(self):
        return self.cards.pop()

    def Shuffle(self):
        np.random.shuffle(self.cards)

    def isEmpty(self):
        return len(self.cards) == 0

    @classmethod
    def generateDeck(cls):
        newCards = []

        for suit, _ in suitList.items():
            for rank, _ in rankList:
                newCards.append(Card(suit, rank))

        deck = cls(newCards)
        deck.Shuffle()

        return deck