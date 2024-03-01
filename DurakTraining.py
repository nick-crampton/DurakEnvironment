from durakNew.game import Game
from durakNew.playerTypes.agentPlayer import AgentPlayer
from durakNew.playerTypes.randomBot import RandomBot
from durakNew.playerTypes.humanPlayer import HumanPlayer
import json
import os
import matplotlib.pyplot as plt

##RL Agent parameters
lrParams = {
    "learningRate": 0.1,
    "discount": 0.99,
    "epsilon": 0.1,
    "deckCount" : 36
}

gameProperties = {
    "handCount" : 6,
    "talonCount" : 24,
    "rankList" : 'd'
}

##Pass array of players with their respective types:
## Human    - 0
## Bot      - 1
## Agent    - 2

trainingIterations = 5000
playerTypes = [2, 1]

def createPlayers(playerTypes, qTable = None, training = True):
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
        elif playerType == 2:
            ##Create AgentPlayer
            newPlayer = AgentPlayer([], i, None, learningRate = lrParams["learningRate"], discount = lrParams["discount"], epsilon = lrParams["epsilon"], qTable = None, isTraining = training)
            pass

        playerList.append(newPlayer)

    return playerList

def playAgent(playerTypes, gameProperties, directory, experimentNo):
    qTable = loadJSON(directory, experimentNo)
    
    createPlayers(playerTypes, qTable, False)

    game = Game(playerList, gameProperties = gameProperties)
    game.newGame()


def runExperiment(trainingIterations, playerList, lrParams, gameProperties, plotIntervals):
    
    gameStats = {
        'survivalCount': 0,
        'durakCount' : 0,
        'totalReward': 0,
        'survivalRates': [] 
    }

    for i in range(trainingIterations):
        print(f"\nGame {i+1}")

        game = Game(playerList, lrParams, gameProperties)
        game.newGame()

        gameStats['survivalCount'] += game.survivalCount
        gameStats['durakCount'] += game.durakCount
        
        tempAgent = game.agent
        
        gameStats['totalReward'] += tempAgent.totalReward
        game.agent.totalReward = 0

        print(f"\nreward accumulated in game is {tempAgent.totalReward}")

        if i % plotIntervals == 0 and i > 0:
            survivalRate = (gameStats['survivalCount'] / i) * 100
            gameStats['survivalRates'].append(survivalRate)

    agent = game.agent

    return gameStats, agent

def saveJSON(qTable, directory, experimentNo):
    
    tableDirectory = os.path.join(directory, 'Q-Tables')
    filepath = os.path.join(tableDirectory, f'experiment_{experimentNo}.json')

    qTableSave = {str(key): value for key, value in qTable.items()}

    with open(filepath, 'w') as file:
        json.dump(qTableSave, file)

def loadJSON(directory, experimentNo):
    tableDirectory = os.path.join(directory, 'Q-Tables')
    filepath = os.path.join(tableDirectory, f'experiment_{experimentNo}.json')

    if not os.path.exists(filepath):
        print(f"No Q-table found at {filepath}")
        return None
    
    with open(filepath, 'r') as file:
        qTableStrKeys = json.load(file)

    qTable = {eval(key): value for key, value in qTableStrKeys.items()}
    return qTable

def plotSurvivalRate(gameStats, interval, experimentNo, directory):
    x = list(range(interval, len(gameStats['survivalRates']) * interval + 1, interval))
    y = gameStats['survivalRates']

    plt.plot(x, y, marker='o')
    plt.xlabel('Number of Games')
    plt.ylabel('Survival Rate (%)')
    plt.title('Survival Rate Over Time')
    plt.ylim(0, 100)  # Set y-axis to range from 0 to 100
    plt.axhline(y=50, color='r', linestyle='--')  # Add a horizontal line at 50%
    plt.grid(True)
    plt.show()

    graphDirectory = os.path.join(directory, 'survival graphs')
    plt.savefig(os.path.join(graphDirectory, f"experiment {experimentNo}.png"))
    print("Experiment graph saved.")

def saveExperimentResults(experimentNo, gameStats, agent, directory):
    filepath = os.path.join(directory, f"experiment_{experimentNo}.txt")
    os.makedirs(directory, exist_ok=True)

    with open(filepath, "w") as file:
        file.write(f"Experiment: {experimentNo}\n")
        file.write(f"Survival Count = {gameStats['survivalCount']}\n")
        file.write(f"Durak Count = {gameStats['durakCount']}\n")
        file.write(f"Total Reward = {gameStats['totalReward']}\n\n")
        file.write("State-Action Pairs, their Q-Values, and the visitation tally:\n")

        sortedQTable = sorted(agent.qTable.keys(), key=lambda k: agent.stateActionCounter.get(k, 0), reverse=True)
        for key in sortedQTable:
            value = agent.qTable[key]
            count = agent.stateActionCounter.get(key, 0)
            
            file.write(f"{key}: {value}, Tally {count}\n")

        '''for key, value in agent.qTable.items():
            
            count = agent.stateActionCounter.get(key, 0)
            file.write(f"{key}: {value}, Tally {count}\n")'''

    print(f"Experiment results saved as {filepath}")

experimentNo = '1b'
intervals = 100

playerList = createPlayers(playerTypes)
##gameStats, agent = runExperiment(trainingIterations, playerList, lrParams, gameProperties, intervals)

targetDirectory = os.path.abspath(os.path.join(os.getcwd(), 'experiments'))

##saveExperimentResults(experimentNo, gameStats, agent, targetDirectory)
##plotSurvivalRate(gameStats, intervals, experimentNo, targetDirectory)

##saveJSON(agent.qTable, targetDirectory, experimentNo)

playAgent(playerTypes, gameProperties, targetDirectory, experimentNo)