from durakNew.game import Game
from durakNew.playerTypes.humanPlayer import HumanPlayer
from durakNew.playerTypes.randomBot import RandomBot
from durakNew.playerTypes.agentPlayer import AgentPlayer

##Pass array of players with their respective types:
## Human    - 0
## Bot      - 1
## Agent    - 2

playerTypes = [1, 1]

##Rank list types
## 'd' = default
## 'm' = rankListM
## 's' = rankListS

gameProperties = {
    "handCount" : 6,
    "talonCount" : 36,
    "rankList" : 'd'
}

def createPlayers(playerTypes):
    playerList = []
    
    for i, playerType in enumerate(playerTypes):
        
        if playerType == 0:
            ##Create HumanPlayer
            newPlayer = HumanPlayer([], i, None)
            pass
        elif playerType == 1:
            ##Create BotPlayer
            newPlayer = RandomBot([], i,  None)
            pass

        playerList.append(newPlayer)
    
    return playerList

playerList = createPlayers(playerTypes)

game = Game(playerList, gameProperties = gameProperties)
game.newGame()
