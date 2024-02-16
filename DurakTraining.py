from durakNew.game import Game
from durakNew.playerTypes.agentPlayer import AgentPlayer
from durakNew.playerTypes.randomBot import RandomBot
from durakNew.playerTypes.humanPlayer import HumanPlayer

##RL Agent parameters
lrParams = {
    "learningRate": 0.1,
    "discount": 0.99,
    "epsilon": 0.1
}

##Pass array of players with their respective types:
## Human    - 0
## Bot      - 1
## Agent    - 2

trainingIterations = 100
playerList = [2, 1]

for i in range(trainingIterations):
    game = Game(playerList, lrParams)