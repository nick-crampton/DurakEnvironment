from durakNew.utils.rankList import rankList
from durakNew.utils.suitList import suitList 

class Card:
    def __init__(self, suit, rank):
        
        if rank not in dict(rankList).keys():
            raise ValueError(f"Invalid rank: {rank}")
        if suit not in suitList:
            raise ValueError(f"Invalid suit: {suit}")
        
        self.suit = suit
        self.rank = rank

    def getRank(self):
        return self.rank
    
    def getSuit(self):
        return self.suit
    
    def __str__(self):
        return (f"{self.rank} of {self.suit}")
    
    def getCardPower(self):
        suitPower = suitList[self.suit]
        rankPower = dict(rankList)[self.rank]

        return (suitPower, rankPower)
