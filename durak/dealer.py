from utils.durakDeck import durakDeck
import numpy as np

class DurakDealer:
    def __init__(self, npRandom):
        self.npRandom = npRandom
        self.deck = durakDeck()
        self.shuffle()

    def shuffle(self):
        self.npRandom.shuffle(self.deck)

    def drawCard(self):
        return self.deck.pop()
    
