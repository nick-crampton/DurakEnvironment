from durakNew.game import Game
from durakNew.playerTypes.agentQ import AgentQ
from durakNew.playerTypes.DQN.agentDQN import AgentDQN
from durakNew.playerTypes.DQN.replayBuffer import ReplayBuffer
from durakNew.playerTypes.randomBot import RandomBot
from durakNew.playerTypes.humanPlayer import HumanPlayer
from durakNew.playerTypes.lowestValueBot import LowestValueBot
import json
import os
import matplotlib.pyplot as plt
import numpy as np

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
            ##Create Q-Learning Agent
            newPlayer = AgentQ([], i, None, learningRate = lrParams["learningRate"], discount = lrParams["discount"], epsilon = lrParams["epsilon"], qTable = None, isTraining = training)
            pass

        elif playerType == 4:
            ##Create DQN Agent
            newPlayer = AgentDQN([], i, None, learningRate = lrParams["learningRate"], discount = lrParams["discount"], epsilon = lrParams["epsilon"], gamma = lrParams["gamma"])

        playerList.append(newPlayer)

    return playerList

def playGame(playerTypes, gameProperties, directory = None, experiment = None):
   
    if experiment is not None:
        directory = os.path.abspath(os.path.join(os.getcwd(), 'experiments'))
        experimentFolder = f"experiment_{experiment}"
        folderDirectory = os.path.join(directory, experimentFolder)
        qTable = loadJSON(folderDirectory, experiment)

        playerList = createPlayers(playerTypes, qTable, False)
    
    else:
        playerList = createPlayers(playerTypes)

    game = Game(playerList, gameProperties = gameProperties)
    game.newGame()

def runExperiment(trainingIterations, playerList, lrParams, gameProperties, intervals, batchSize = None, metadataTotal = None, metadataPhase = None):
    
    if metadataTotal is None:
        gameStatsTotal = {
        'trainingCount' : 0,
        'survivalCount': 0,
        'gameLength': 0,
        'durakCount' : 0,
        'totalReward': 0,
        'averageReward': [],
        'averageRewardInterval': [],
        'survivalRates': [],
        'survivalRatesInterval' : [],
        'averageGameLength' : [],
        'averageGameLengthInterval' : []
        }

        gameStatsPhase = {
        'trainingCount' : 0,
        'survivalCount': 0,
        'gameLength': 0,
        'durakCount' : 0,
        'totalReward': 0,
        'averageReward': [],
        'averageRewardInterval': [],
        'survivalRates': [],
        'survivalRatesInterval' : [],
        'averageGameLength' : [],
        'averageGameLengthInterval' : []
        }

    elif metadataPhase is None:
        gameStatsTotal = metadataTotal

        gameStatsPhase = {
        'trainingCount' : 0,
        'survivalCount': 0,
        'gameLength': 0,
        'durakCount' : 0,
        'totalReward': 0,
        'averageReward': [],
        'averageRewardInterval': [],
        'survivalRates': [],
        'survivalRatesInterval' : [],
        'averageGameLength' : [],
        'averageGameLengthInterval' : []
        }

    else:
        gameStatsTotal = metadataTotal
        gameStatsPhase = metadataPhase

    survivalCountInterval = 0
    totalRewardInterval = 0
    gameLengthInterval = 0

    for i in range(trainingIterations):
        print(f"\nGame {i+1}")

        game = Game(playerList, lrParams, gameProperties)
        game.newGame()

        ##Add gameStats for an overall graph
        gameStatsTotal['trainingCount'] += 1
        gameStatsTotal['survivalCount'] += game.survivalCount
        gameStatsTotal['durakCount'] += game.durakCount
        gameStatsTotal['gameLength'] += game.gameLength

        ##Add gameStats for a graph for just this stage of training
        gameStatsPhase['trainingCount'] += 1
        gameStatsPhase['survivalCount'] += game.survivalCount
        gameStatsPhase['durakCount'] += game.durakCount
        gameStatsPhase['gameLength'] += game.gameLength
 
        survivalCountInterval += game.survivalCount
        gameLengthInterval += game.gameLength

        tempAgent = game.agent
        
        gameStatsTotal['totalReward'] += tempAgent.totalReward
        gameStatsPhase['totalReward'] += tempAgent.totalReward

        totalRewardInterval += tempAgent.totalReward

        print(f"\nReward accumulated in game is {tempAgent.totalReward}")
        game.agent.totalReward = 0

        if len(tempAgent.replayBuffer) >= batchSize:
            print("Gameplay halted, neural network is training...")
            tempAgent.trainNetwork()
            


        if (i + 1) % intervals == 0 and i > 0:
            ##Survival Rates
            survivalRateTotal = (gameStatsTotal['survivalCount'] / gameStatsTotal['trainingCount']) * 100
            gameStatsTotal['survivalRates'].append(survivalRateTotal)

            survivalRatePhase = (gameStatsPhase['survivalCount'] / gameStatsPhase['trainingCount']) * 100
            gameStatsPhase['survivalRates'].append(survivalRatePhase)

            survivalRateInterval = (survivalCountInterval / intervals) * 100
            gameStatsTotal['survivalRatesInterval'].append(survivalRateInterval)
            gameStatsPhase['survivalRatesInterval'].append(survivalRateInterval)

            survivalCountInterval = 0

            ##Average Reward
            averageRewardTotal = (gameStatsTotal['totalReward'] / gameStatsTotal['trainingCount'])
            gameStatsTotal['averageReward'].append(averageRewardTotal)

            averageRewardPhase = (gameStatsPhase['totalReward'] / gameStatsPhase['trainingCount'])
            gameStatsPhase['averageReward'].append(averageRewardPhase)

            averageRewardInterval = (totalRewardInterval / intervals)
            
            gameStatsTotal['averageRewardInterval'].append(averageRewardInterval)
            gameStatsPhase['averageRewardInterval'].append(averageRewardInterval)

            totalRewardInterval = 0

            ##Average Game Length
            avgGameLengthTotal = (gameStatsTotal['gameLength'] / gameStatsTotal['trainingCount'])
            gameStatsTotal['averageGameLength'].append(avgGameLengthTotal)

            avgGameLengthPhase = (gameStatsPhase['gameLength'] / gameStatsPhase['trainingCount'])
            gameStatsPhase['averageGameLength'].append(avgGameLengthPhase)

            avgGameLengthInterval = (gameLengthInterval / intervals)
            gameStatsTotal['averageGameLengthInterval'].append(avgGameLengthInterval)
            gameStatsPhase['averageGameLengthInterval'].append(avgGameLengthInterval)

            gameLengthInterval = 0

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

def loadMetadata(directory, experiment = None, phase = None):
    metadataDirectory = os.path.join(directory, 'Metadata')
    if experiment is not None:
        filepath = os.path.join(metadataDirectory, f'Metadata_experiment_{experiment}')

    else:
        filepath = os.path.join(metadataDirectory, f'Metadata_phase_{phase}')

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

def loadJSON(directory, experiment):
    tableDirectory = os.path.join(directory, 'Q-Tables')
    filepath = os.path.join(tableDirectory, f'experiment_{experiment}.json')

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

    xIntervals = list(range(interval, len(gameStats['survivalRatesInterval']) * interval + 1, interval))
    yIntervals = gameStats['survivalRatesInterval']

    ##Linear Regression of intervals
    zInterval = np.polyfit(xIntervals, yIntervals, 1)
    pFunc = np.poly1d(zInterval)

    plt.plot(xTotal, yTotal, marker=',', color = 'r', label = "Overall Survival Rate")
    plt.plot(xIntervals, yIntervals, marker = ',', color = 'b', label = 'Interval Survival Rate')
    plt.plot(xIntervals, pFunc(xIntervals), linestyle = 'dashed', color = '#AAFF00', label = "Interval Survival Rate Trend")

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

    xIntervals = list(range(interval, len(gameStats['averageRewardInterval']) * interval + 1, interval))
    yIntervals = gameStats['averageRewardInterval']

    ##Linear Regression of intervals
    zInterval = np.polyfit(xIntervals, yIntervals, 1)
    pFunc = np.poly1d(zInterval)

    plt.plot(xTotal, yTotal, marker=',', color = 'r', label = "Overall Average Reward")
    plt.plot(xIntervals, yIntervals, marker = ',', color = 'b', label = 'Interval Average Reward')
    plt.plot(xIntervals, pFunc(xIntervals), linestyle = 'dashed', color = '#AAFF00', label = "Interval Average Reward Trend")

    plt.xlabel("Number of Games")
    plt.ylabel('Average Reward')

    if phase is None:
        plt.title(f'Average Reward Over Total Training - Experiment {experiment}')
        filename = f"Average_reward_experiment_{experiment}.png"

    else:
        plt.title(f'Average Reward Over Phase {phase} - Experiment {experiment}')
        filename = f"Average_reward_experiment_{experiment}_phase_{phase}.png"
    
    plt.axhline(y = 0, color = 'g')
    plt.ylim(-0.5, 2)
    plt.grid(True)
    plt.legend()

    graphDirectory = os.path.join(directory, 'reward graphs')
    os.makedirs(graphDirectory, exist_ok=True)

    filepath = os.path.join(graphDirectory, filename)

    plt.savefig(filepath)
    print("Reward graph saved.")
    plt.close()

def plotAverageGameLength(gameStats, interval, experiment, directory, phase = None):

    xTotal = list(range(interval, len(gameStats['averageGameLength']) * interval + 1, interval))
    yTotal = gameStats['averageGameLength']

    xIntervals = list(range(interval, len(gameStats['averageGameLengthInterval']) * interval + 1, interval))
    yIntervals = gameStats['averageGameLengthInterval']    

    ##Linear Regression of intervals
    zInterval = np.polyfit(xIntervals, yIntervals, 1)
    pFunc = np.poly1d(zInterval)

    plt.plot(xTotal, yTotal, marker=',', color = 'r', label = "Experiment Average Game Length")
    plt.plot(xIntervals, yIntervals, marker = ',', color = 'b', label = 'Interval Average Game Length')
    plt.plot(xIntervals, pFunc(xIntervals), linestyle = 'dashed', color = '#AAFF00', label = "Interval Average Game Length Trend")

    plt.xlabel("Number of Games")
    plt.ylabel('Average Game Length')

    if phase is None:
        plt.title(f'Average Game Length Over Total Training - Experiment {experiment}')
        filename = f"Average_game_length_experiment_{experiment}.png"

    else:
        plt.title(f'Average Game Length Over Phase {phase} - Experiment {experiment}')
        filename = f"Average_game_length_experiment_{experiment}_phase_{phase}.png"
    
    plt.ylim(10, 20)
    plt.grid(True)
    plt.legend() 

    graphDirectory = os.path.join(directory, 'game length graphs')
    os.makedirs(graphDirectory, exist_ok=True)

    filepath = os.path.join(graphDirectory, filename)

    plt.savefig(filepath)
    print("Game length graph saved.")
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

    ##Plot average game lengths
    plotAverageGameLength(gameStatsTotal, intervals, experiment, folderPath)
    plotAverageGameLength(gameStatsPhase, intervals, experiment, folderPath, phase)
    
    ##Save the Q-Table, and the Metadata
    saveJSON(agent.qTable, folderPath, experiment)
    saveMetadata(gameStatsTotal, folderPath, experiment = experiment)
    saveMetadata(gameStatsPhase, folderPath, phase = phase)

def determinePlayerTypes(phase):
    ##Pass array of players with their respective types:
    ## Human            - 0
    ## RandomBot        - 1
    ## LowestValueBot   - 2
    ## Q Agent          - 3
    ## DQN Agent        - 4

    if phase == "A":
        playerTypes = [3, 1]

    elif phase == "B":
        playerTypes = [3, 2]

    return playerTypes

def agentTraining(experiment, phase, lrParams, gameProperties, intervals, trainingIterations):
    
    ##Results are stored in experiments folder
    directory = os.path.abspath(os.path.join(os.getcwd(), 'experiments'))

    ##Get the playerTypes given the phase of training we are in
    playerTypes = determinePlayerTypes(phase)

    ##Loads the qTable of the agent, if it exists
    experimentFolder = f"experiment_{experiment}"
    folderDirectory = os.path.join(directory, experimentFolder)

    qTable = loadJSON(folderDirectory, experiment)

    if qTable is not None:
        totalMetadata = loadMetadata(folderDirectory, experiment = experiment)
        phaseMetadata = loadMetadata(folderDirectory, phase = phase)
        playerList = createPlayers(playerTypes, qTable)
        gameStatsTotal, gameStatsPhase, agent = runExperiment(trainingIterations, playerList, lrParams, gameProperties, intervals, totalMetadata, phaseMetadata)

    else:
        playerList = createPlayers(playerTypes)
        gameStatsTotal, gameStatsPhase, agent = runExperiment(trainingIterations, playerList, lrParams, gameProperties, intervals)

    saveExperimentFolder(experiment, phase, gameStatsTotal, gameStatsPhase, lrParams, gameProperties, agent, directory)

experiment = '1'
phase = 'B'
intervals = 500
trainingIterations = 100000

##RL Agent parameters
lrParams = {
    "learningRate": 0.1,
    "discount": 0.99,
    "epsilon": 0.1,
    "gamma" : 0,
    "batchSize" : 128,
    "inputSize" : 1374,
    "outputSize" : 506
}

gameProperties = {
    "handCount" : 6,
    "talonCount" : 36,
    "printGameplay" : True
}

##Phases:
## A - RandomBot Training
## B - LowestValueBot Training
## C - 3 Player Matches

##agentTraining(experiment, phase, lrParams, gameProperties, intervals, trainingIterations)

playGame([3, 1], gameProperties)