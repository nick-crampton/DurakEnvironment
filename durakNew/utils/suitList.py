suitList = {
    "Hearts": 0,
    "Diamonds": 1,
    "Spades": 2,
    "Clubs": 3
}

def getKeyFromValue(suitList, value):
    for key, val in suitList.items():
        if val == value:
            return key
    return None