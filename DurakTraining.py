from durakNew.game import Game
from durakNew.playerTypes.agentPlayer import AgentPlayer
from durakNew.playerTypes.randomBot import RandomBot
from durakNew.playerTypes.humanPlayer import HumanPlayer
from durakNew.playerTypes.lowestValueBot import LowestValueBot
import json
import os
import matplotlib.pyplot as plt



def createPlayers(playerTypes, qTable = None, training = True):
    playerList = []
        
    for i, playerType in enumerate(playerTypes):
        
        if playerType == 0:
            ##Create HumanPlayer
            newPlayer = HumanPlayer([], i, None)
            pass
        
        elif playerType == 1:
            ##Create RandomBot
            newPlayer = RandomBot([], i,  None)
            pass
        
        elif playerType == 2:
            ##Create LowestValueBot
            newPlayer = LowestValueBot([], i, None)
            pass
        
        elif playerType == 3:
            ##Create AgentPlayer
            newPlayer = AgentPlayer([], i, None, learningRate = lrParams["learningRate"], discount = lrParams["discount"], epsilon = lrParams["epsilon"], qTable = None, isTraining = training)
            pass

        playerList.append(newPlayer)

    return playerList

def playAgent(playerTypes, gameProperties, directory, experimentNo):
    qTable = loadJSON(directory, experimentNo)
    
    playerList = createPlayers(playerTypes, qTable, False)

    game = Game(playerList, gameProperties = gameProperties)
    game.newGame()

def runExperiment(trainingIterations, playerList, lrParams, gameProperties, intervals, metadataTotal = None, metadataPhase = None):
    
    if metadataTotal is None:
        gameStatsTotal = {
        'trainingCount' : 0,
        'survivalCount': 0,
        'durakCount' : 0,
        'totalReward': 0,
        'averageReward': [],
        'averageRewardInterval': [],
        'survivalRates': [],
        'survivalRatesInterval' : []
        }

        gameStatsPhase = {
        'trainingCount' : 0,
        'survivalCount': 0,
        'durakCount' : 0,
        'totalReward': 0,
        'averageReward': [],
        'averageRewardInterval': [],
        'survivalRates': [],
        'survivalRatesInterval' : []
        }

    else:
        gameStatsTotal = metadataTotal
        gameStatsPhase = metadataPhase

    survivalCountInterval = 0
    totalRewardInterval = 0

    for i in range(trainingIterations):
        print(f"\nGame {i+1}")

        game = Game(playerList, lrParams, gameProperties)
        game.newGame()

        ##Add gameStats for an overall graph
        gameStatsTotal['trainingCount'] += 1
        gameStatsTotal['survivalCount'] += game.survivalCount
        gameStatsTotal['durakCount'] += game.durakCount

        ##Add gameStats for a graph for just this stage of training
        gameStatsPhase['trainingCount'] += 1
        gameStatsPhase['survivalCount'] += game.survivalCount
        gameStatsPhase['durakCount'] += game.durakCount
        
        survivalCountInterval += game.survivalCount

        tempAgent = game.agent
        
        gameStatsTotal['totalReward'] += tempAgent.totalReward
        gameStatsPhase['totalReward'] += tempAgent.totalReward

        totalRewardInterval += tempAgent.totalReward

        game.agent.totalReward = 0

        print(f"\nReward accumulated in game is {tempAgent.totalReward}")

        if i % intervals == 0 and i > 0:
            survivalRateTotal = (gameStatsTotal['survivalCount'] / gameStatsTotal['trainingCount']) * 100
            gameStatsTotal['survivalRates'].append(survivalRateTotal)

            survivalRatePhase = (gameStatsPhase['survivalCount'] / gameStatsPhase['trainingCount']) * 100
            gameStatsPhase['survivalRates'].append(survivalRatePhase)

            survivalRateInterval = (survivalCountInterval / intervals) * 100
            gameStatsTotal['survivalRatesInterval'].append(survivalRateInterval)
            gameStatsPhase['survivalRatesInterval'].append(survivalRateInterval)

            survivalCountInterval = 0

            averageRewardTotal = (gameStatsTotal['TotalReward'] / gameStatsTotal['trainingCount'])
            gameStatsTotal['averageReward'].append(averageRewardTotal)

            averageRewardPhase = (gameStatsPhase['TotalReward'] / gameStatsPhase['trainingCount'])
            gameStatsPhase['averageReward'].append(averageRewardPhase)

            averageRewardInterval = (totalRewardInterval / intervals)
            
            gameStatsTotal['averageRewardIntervals'].append(averageRewardInterval)
            gameStatsPhase['averageRewardIntervals'].append(averageRewardInterval)

    agent = game.agent

    return gameStatsTotal, gameStatsPhase, agent

def saveMetadata(metadata, directory, experiment = None, phase = None):
    metadataDirectory = os.path.join(directory, 'Metadata')
    os.makedirs(metadataDirectory, exist_ok=True)

    if phase is None:
        filename = f"Metadata_experiment_{experiment}"

    elif experiment is None:
        filename = f"Metadata_phase_{phase}"

    filepath = os.path.join(metadataDirectory, filename)

    with open(filepath, 'w') as file:
        json.dump(metadata, file)

def loadMetadata(directory, experimentNo):
    metadataDirectory = os.path.join(directory, 'Metadata')
    filepath = os.path.join(metadataDirectory, f'metadata_{experimentNo}.json')

    if not os.path.exists(filepath):
        print(f"No metadata found at {filepath}")
        return None
    
    with open(filepath, 'r') as file:
        metadata = json.load(file)

    return metadata

def saveJSON(qTable, directory, experimentNo):
    tableDirectory = os.path.join(directory, 'Q-Tables')
    os.makedirs(tableDirectory, exist_ok=True)

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

def plotSurvivalRate(gameStats, interval, experiment, directory, phase = None):

    xTotal = list(range(interval, len(gameStats['survivalRates']) * interval + 1, interval))
    yTotal = gameStats['survivalRates']

    xIntervals = list(range(interval), len(gameStats['survivalRatesInterval'] * interval + 1, interval))
    yIntervals = gameStats['survivalRatesInterval']

    plt.plot(xTotal, yTotal, marker='o', color = 'b', label = "Overall Survival Rate")
    plt.plot(xIntervals, yIntervals, marker = 'o', color = 'r', label = 'Interval Survival Rate')
    
    plt.xlabel('Number of Games')
    plt.ylabel('Survival Rate (%)')
    
    if phase is None:
        plt.title('Survival Rate Over Total Training - Experiment {experiment}')
        filename = f"Survival_experiment_{experiment}.png"

    else:
        plt.title(f'Survival Rate Over Phase {phase} - Experiment {experiment}')
        filename = f"Survival_experiment_{experiment}_phase_{phase}.png"
    
    plt.ylim(0, 100)
    plt.axhline(y=50, color='g', linestyle='--')  
    plt.grid(True)
    plt.legend()
    
    graphDirectory = os.path.join(directory, 'survival graphs')
    os.makedirs(graphDirectory, exist_ok=True)

    filepath = os.path.join(graphDirectory, filename)

    plt.savefig(filepath)
    print("Survival graph saved.")
    plt.close()

def plotAverageRewards(gameStats, interval, experiment, directory, phase = None):

    xTotal = list(range(interval, len(gameStats['averageReward']) * interval + 1, interval))
    yTotal = gameStats['averageReward']

    xIntervals = list(range(interval), len(gameStats['averageRewardInterval'] * interval + 1, interval))
    yIntervals = gameStats['averageRewardInterval']

    plt.plot(xTotal, yTotal, marker='o', color = 'b', label = "Overall Average Reward")
    plt.plot(xIntervals, yIntervals, marker = 'o', color = 'r', label = 'Interval Average Reward')

    plt.xlabel("Number of Games")
    plt.ylabel('Average Reward')

    if phase is None:
        plt.title('Average Reward Over Total Training - Experiment {experiment}')
        filename = f"Average_reward_experiment_{experiment}.png"

    else:
        plt.title(f'Average Reward Over Phase {phase} - Experiment {experiment}')
        filename = f"Average_reward_experiment_{experiment}_phase_{phase}.png"

    plt.ylim(-50, 50)
    plt.axhline(y = 0, color = 'g', linestyle = '--')
    plt.grid = True
    plt.legend()

    graphDirectory = os.path.join(directory, 'reward graphs')
    os.makedirs(graphDirectory, exist_ok=True)

    filepath = os.path.join(graphDirectory, filename)

    plt.savefig(filepath)
    print("Reward graph saved.")
    plt.close()

def saveExperimentResults(experimentNo, gameStats, lrParams, gameProperties, agent, directory):
    filepath = os.path.join(directory, f"experiment_{experimentNo}.txt")
    os.makedirs(directory, exist_ok=True)

    with open(filepath, "w") as file:
        file.write(f"Experiment: {experimentNo}\n")
        file.write(f"Survival Count = {gameStats['survivalCount']}\n")
        file.write(f"Durak Count = {gameStats['durakCount']}\n")
        file.write(f"Total Reward = {gameStats['totalReward']}\n")

        file.write(f"\nReinforcement Learning Parameters\n")
        for key, value in lrParams.items():
            file.write(f"{key}: {value}\n")
            
        file.write('\nGame Properties\n')

        for key, value in gameProperties.items():
            file.write(f"{key}: {value}\n")
            

        file.write("\nState-Action Pairs, their Q-Values, and the visitation tally:\n")

        sortedQTable = sorted(agent.qTable.keys(), key=lambda k: agent.stateActionCounter.get(k, 0), reverse=True)
        for key in sortedQTable:
            value = agent.qTable[key]
            count = agent.stateActionCounter.get(key, 0)
            
            file.write(f"{key}: {value}, Tally {count}\n")

    print(f"Experiment results saved as {filepath}")

def writeFile(directory, filename, gameStats, lrParams, gameProperties, agent):
    logDirectory = os.path.join(directory, 'logs')
    os.makedirs(logDirectory, exist_ok=True)

    filepath = os.path.join(logDirectory, filename)

    with open(filepath, "w") as file:
        file.write(f"{filename}\n")
        file.write(f"Survival Count = {gameStats['survivalCount']}\n")
        file.write(f"Durak Count = {gameStats['durakCount']}\n")
        file.write(f"Total Reward = {gameStats['totalReward']}\n")
        file.write(f"Average Reward = {gameStats['averageReward']}\n")

        file.write(f"\nReinforcement Learning Parameters\n")
        for key, value in lrParams.items():
            file.write(f"{key}: {value}\n")
            
        file.write('\nGame Properties\n')

        for key, value in gameProperties.items():
            file.write(f"{key}: {value}\n")
            
        file.write("\nState-Action Pairs, their Q-Values, and the visitation tally:\n")

        sortedQTable = sorted(agent.qTable.keys(), key=lambda k: agent.stateActionCounter.get(k, 0), reverse=True)
        for key in sortedQTable:
            value = agent.qTable[key]
            count = agent.stateActionCounter.get(key, 0)
            
            file.write(f"{key}: {value}, Tally {count}\n")

    print(f"Experiment results saved as {filename}")

def saveExperimentFolder(experiment, phase, gameStatsTotal, gameStatsPhase, lrParams, gameProperties, agent, directory):
    ##Specify folder, create it if doesn't exist
    experimentFolder = f"experiment_{experiment}"
    folderPath = os.path.join(directory, experimentFolder)
    os.makedirs(folderPath, exist_ok = True)

    ##Save the log files of the phases and the entire training.
    filenameTotal = f"experiment_{experiment}.txt"
    filenamePhase = f"phase_{phase}.txt"

    writeFile(folderPath, filenameTotal, gameStatsTotal, lrParams, gameProperties, agent)
    writeFile(folderPath, filenamePhase, gameStatsPhase, lrParams, gameProperties, agent)

    ##Plot the survival rates for both the phase and total training
    plotSurvivalRate(gameStatsTotal, intervals, experiment, folderPath)
    plotSurvivalRate(gameStatsPhase, intervals, experiment, folderPath, phase)

    ##Plot the average reward over time
    plotAverageRewards(gameStatsTotal, intervals, experiment, folderPath)
    plotAverageRewards(gameStatsPhase, intervals, experiment, folderPath, phase)
    
    ##Save the Q-Table, and the Metadata
    saveJSON(agent.qTable, folderPath, experiment)
    saveMetadata(gameStatsTotal, folderPath, experiment = experiment)
    saveMetadata(gameStatsPhase, folderPath, phase = phase)

def determinePlayerTypes(phase):
    ##Pass array of players with their respective types:
    ## Human            - 0
    ## RandomBot        - 1
    ## LowestValueBot   - 2
    ## Agent            - 3

    if phase is "A":
        playerTypes = [3, 1]

    elif phase is "B":
        playerTypes = [3, 2]

    return playerTypes

def agentTraining(experiment, phase, lrParams, gameProperties, intervals, trainingIterations):
    
    ##Results are stored in experiments folder
    directory = os.path.abspath(os.path.join(os.getcwd(), 'experiments'))

    ##Get the playerTypes given the phase of training we are in
    playerTypes = determinePlayerTypes(phase)

    ##Loads the qTable of the agent, if it exists
    qTable = loadJSON(directory, experiment)

    if qTable is not None:
        totalMetadata = loadMetadata(targetDirectory, experimentName)
        phaseMetadata = loadMetadata(targetDirectory, phaseName)
        playerList = createPlayers(playerTypes, qTable)
        gameStatsTotal, gameStatsPhase, agent = runExperiment(trainingIterations, playerList, lrParams, gameProperties, intervals, totalMetadata, phaseMetadata)

    else:
        playerList = createPlayers(playerTypes)
        gameStatsTotal, gameStatsPhase, agent = runExperiment(trainingIterations, playerList, lrParams, gameProperties, intervals)

    saveExperimentFolder(experiment, phase, gameStatsTotal, gameStatsPhase, lrParams, gameProperties, agent, directory)

experiment = '1'
phase = 'A'
intervals = 1000
trainingIterations = 10000

##RL Agent parameters
lrParams = {
    "learningRate": 0.1,
    "discount": 0.99,
    "epsilon": 0.1,
}

gameProperties = {
    "handCount" : 3,
    "talonCount" : 12,
    "rankList" : 'd'
}

##Phases:
## A - RandomBot Training
## B - LowestValueBot Training
## C - 3 Player Matches

agentTraining(experiment, phase, lrParams, gameProperties, intervals, trainingIterations)
##playAgent(playerTypes, gameProperties, targetDirectory, experimentNo)