from durakNew.game import Game
from durakNew.playerTypes.agent import Agent
from durakNew.playerTypes.agentQ import AgentQ
from durakNew.playerTypes.DQN.agentDQN import AgentDQN
from durakNew.playerTypes.DQN.replayBuffer import ReplayBuffer
from durakNew.playerTypes.DQN.training import DQN
from durakNew.playerTypes.randomBot import RandomBot
from durakNew.playerTypes.humanPlayer import HumanPlayer
from durakNew.playerTypes.lowestValueBot import LowestValueBot

import json
import os
import matplotlib.pyplot as plt
import numpy as np
import torch

print(torch.cuda.is_available())  
print(torch.version.cuda)         
print(torch.cuda.current_device())
print(torch.cuda.device_count())
print(torch.cuda.get_device_name(0)) 

def createPlayers(playerTypes, training):
    global directory
    
    playerList = []
    metadataList = []

    if not (2 <= len(playerTypes) <= 6):
        raise ValueError("Player count must be between 2 - 6!")
    
    for i, player in enumerate(playerTypes):
        if isinstance(player, int):

            if player == 0:
                newPlayer = HumanPlayer([], i, None)
                metadataList.append(None)

            elif player == 1:
                newPlayer = RandomBot([], i, None)
                metadataList.append(None)
            
            elif player == 2:
                newPlayer = LowestValueBot([], i, None)
                metadataList.append(None)

        elif isinstance(player, dict):
            experiment = player['experiment']
            phase = player['phase']
            parameters = player['parameters']
            
            experimentFolder = f"experiment_{experiment}"
            
            if player["type"] == 3: 
                agentTypeDirectory = "Q"
                agentFolder = os.path.join(directory, agentTypeDirectory, experimentFolder)

                qTable = loadQTable(agentFolder, experiment)
                if qTable is not None:
                    totalMetadata = loadMetadata(agentFolder, experiment = experiment)
                    phaseMetadata = loadMetadata(agentFolder, phase = phase)
                    
                    metadataList.append((totalMetadata, phaseMetadata))
                
                else:
                    metadataList.append(None)

                newPlayer = AgentQ([], i, None, parameters, qTable, training)

            elif player["type"] == 4: 
                agentTypeDirectory = "DQN"
                agentFolder = os.path.join(directory, agentTypeDirectory, experimentFolder)

                model = loadModel(directory, experiment, parameters['inputSize'], parameters['outputSize'])
                replayBuffer = loadReplayBuffer(agentFolder, experiment)
                if model is not None or replayBuffer is not None:
                    totalMetadata = loadMetadata(agentFolder, experiment = experiment)
                    phaseMetadata = loadMetadata(agentFolder, phase = phase)

                    metadataList.append((totalMetadata, phaseMetadata))
                
                else:
                    metadataList.append(None)

                newPlayer = AgentDQN([], i, None, parameters, model, replayBuffer)

        playerList.append(newPlayer)
    
    return playerList, metadataList 
                
def playGame(playerTypes, gameProperties, directory = None, experiment = None):
   
    if experiment is not None:
        directory = os.path.abspath(os.path.join(os.getcwd(), 'experiments'))
        experimentFolder = f"experiment_{experiment}"
        folderDirectory = os.path.join(directory, experimentFolder)
        qTable = loadQTable(folderDirectory, experiment)

        playerList = createPlayers(playerTypes, qTable, False)
    
    else:
        playerList, _ = createPlayers(playerTypes, False)

    game = Game(playerList, gameProperties)
    game.newGame()

def runExperiment(playerList, metadataList, gameProperties, analysisIntervals, trainingIterations):
    
    agentsStats = [{'total': None, 'phase': None, 'interval': {'survivalCount': 0, 'totalReward': 0, 'gameLength': 0}} for i in playerList]
    
    for i, (agent, metadata) in enumerate(zip(playerList, metadataList)):

        if isinstance(agent, Agent):
            
            if metadata is None or metadata[0] is None:
                agentsStats[i]['total'] = {
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
                agentsStats[i]['total'] = metadata[0]

            if metadata is None or (len(metadata) > 1 and metadata[1] is None):
                agentsStats[i]['phase'] = {
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
                agentsStats[i]['phase'] = metadata[1] 
        
        else:
            agentsStats[i] = None

    for i in range(trainingIterations):
        print(f"\nGame {i+1}")

        game = Game(playerList, gameProperties)
        game.newGame()

        playerList = sorted(playerList, key=lambda player: player.playerID)

        for j, agent in enumerate(playerList):
            if isinstance(agent, Agent):

                agentStats = agentsStats[j]
                intervalAnalysis = agentsStats[j]['interval']

                ##Add gameStats for an overall graph
                agentStats['total']['trainingCount'] += 1
                agentStats['total']['survivalCount'] += agent.survivalCount
                agentStats['total']['durakCount'] += agent.durakCount
                agentStats['total']['gameLength'] += game.gameLength
                agentStats['total']['totalReward'] += agent.totalReward

                ##Add gameStats for a graph for just this stage of training
                agentStats['phase']['trainingCount'] += 1
                agentStats['phase']['survivalCount'] += agent.survivalCount
                agentStats['phase']['durakCount'] += agent.durakCount
                agentStats['phase']['gameLength'] += game.gameLength
                agentStats['phase']['totalReward'] += agent.totalReward
        
                intervalAnalysis['survivalCount'] += agent.survivalCount
                intervalAnalysis['gameLength'] += game.gameLength
                intervalAnalysis['totalReward'] += agent.totalReward

                agent.survivalCount = 0
                agent.durakCount = 0
                
                print(f"\nReward accumulated in game is {agent.totalReward}")
                agent.totalReward = 0

        for agent in playerList:
            if isinstance(agent, AgentDQN):
                if (i +  1) % agent.trainingIntervals == 0:
                    print(f"Training neural network of player {agent.playerID}")

                    if len(agent.replayBuffer) >= agent.batchSize:
                        agent.trainNetwork()
                                
        if (i + 1) % analysisIntervals == 0 and i > 0:
            
            for agentStats in agentsStats:
                if agentStats is None:
                    continue

                ##Survival Rates
                survivalRateTotal = (agentStats['total']['survivalCount'] / agentStats['total']['trainingCount']) * 100
                agentStats['total']['survivalRates'].append(survivalRateTotal)

                survivalRatePhase = (agentStats['phase']['survivalCount'] / agentStats['phase']['trainingCount']) * 100
                agentStats['phase']['survivalRates'].append(survivalRatePhase)

                survivalRateInterval = (agentStats['interval']['survivalCount'] / analysisIntervals) * 100
                agentStats['total']['survivalRatesInterval'].append(survivalRateInterval)
                agentStats['phase']['survivalRatesInterval'].append(survivalRateInterval)

                agentStats['interval']['survivalCount'] = 0

                ##Average Reward
                averageRewardTotal = (agentStats['total']['totalReward'] / agentStats['total']['trainingCount'])
                agentStats['total']['averageReward'].append(averageRewardTotal)

                averageRewardPhase = (agentStats['phase']['totalReward'] / agentStats['phase']['trainingCount'])
                agentStats['phase']['averageReward'].append(averageRewardPhase)

                averageRewardInterval = (agentStats['interval']['totalReward'] / analysisIntervals)
                
                agentStats['total']['averageRewardInterval'].append(averageRewardInterval)
                agentStats['phase']['averageRewardInterval'].append(averageRewardInterval)

                agentStats['interval']['totalReward'] = 0

                ##Average Game Length
                avgGameLengthTotal = (agentStats['total']['gameLength'] / agentStats['total']['trainingCount'])
                agentStats['total']['averageGameLength'].append(avgGameLengthTotal)

                avgGameLengthPhase = (agentStats['phase']['gameLength'] / agentStats['phase']['trainingCount'])
                agentStats['phase']['averageGameLength'].append(avgGameLengthPhase)

                avgGameLengthInterval = (agentStats['interval']['gameLength'] / analysisIntervals)
                agentStats['total']['averageGameLengthInterval'].append(avgGameLengthInterval)
                agentStats['phase']['averageGameLengthInterval'].append(avgGameLengthInterval)

                agentStats['interval']['gameLength'] = 0

    return playerList, agentsStats

def saveModel(model, directory, experiment):
    modelDirectory = os.path.join(directory, 'Model')
    os.makedirs(modelDirectory, exist_ok=True)

    filepath = os.path.join(modelDirectory, experiment)
    torch.save(model.state_dict(), filepath)
    print(f"Model saved to {filepath}")

def loadModel(directory, experiment, inputSize, outputSize):
    modelDirectory = os.path.join(directory, 'Model')
    
    filename = f"model_experiment_{experiment}.pth"
    filepath = os.path.join(modelDirectory, filename)
    
    if not os.path.isfile(filepath):
        print(f"No model found at {filepath}")
        model = DQN(inputSize, outputSize)
    
    else:
        model = DQN(inputSize, outputSize)
        model.load_state_dict(torch.load(filepath, map_location=device))
        print(f"Model loaded from {filepath}")
    
    return model

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

def saveQTable(qTable, directory, experimentNo):
    tableDirectory = os.path.join(directory, 'Q-Tables')
    os.makedirs(tableDirectory, exist_ok=True)

    filepath = os.path.join(tableDirectory, f'experiment_{experimentNo}.json')

    qTableSave = {str(key): value for key, value in qTable.items()}

    with open(filepath, 'w') as file:
        json.dump(qTableSave, file)

def loadQTable(directory, experiment):
    tableDirectory = os.path.join(directory, 'Q-Tables')
    filepath = os.path.join(tableDirectory, f'experiment_{experiment}.json')

    if not os.path.exists(filepath):
        print(f"No Q-table found at {filepath}, creating a new one")
        return None
    
    with open(filepath, 'r') as file:
        qTableStrKeys = json.load(file)

    qTable = {eval(key): value for key, value in qTableStrKeys.items()}
    return qTable

def saveReplayBuffer(replayBuffer, directory, experiment):
    bufferDirectory = os.path.join(directory, 'Replay Buffers')
    os.makedirs(bufferDirectory, exist_ok = True)

    filepath = os.path.join(bufferDirectory, f'experiment_{experiment}.json')
    
    data = {
        "capacity" : replayBuffer.capacity,
        "buffer" : replayBuffer.buffer,
        "position" : replayBuffer.position
    }

    with open(filepath, "w") as f:
        json.dump(data, f)

    print(f"Replay buffer saved to {filepath}")

def loadReplayBuffer(directory, experiment):
    bufferDirectory = os.path.join(directory, 'Replay Buffers')
    filepath = os.path.join(bufferDirectory, f"experiment_{experiment}.json")
    
    if not os.path.exists(filepath):
        print(f"No replay buffer found at {filepath}. Starting a new buffer.")
        return None
    
    with open(filepath, "r") as f:
        data = json.load(f)
    
    replayBuffer = ReplayBuffer(data["capacity"])
    replayBuffer.buffer = data["buffer"]
    replayBuffer.position = data["position"]
    
    print(f"Replay buffer loaded from {filepath}")
    return replayBuffer

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
    
    plt.ylim(0, 50)
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

        if isinstance(agent, AgentQ):    
            file.write("\nState-Action Pairs, their Q-Values, and the visitation tally:\n")

            sortedQTable = sorted(agent.qTable.keys(), key=lambda k: agent.stateActionCounter.get(k, 0), reverse=True)
            for key in sortedQTable:
                value = agent.qTable[key]
                count = agent.stateActionCounter.get(key, 0)
                
                file.write(f"{key}: {value}, Tally {count}\n")
        
        elif isinstance(agent, AgentDQN):
            file.write("\nModel Loss:\n")
            for i, loss in enumerate(agent.modelLosses):
                file.write(f"Training episode {i} - Loss: {loss}\n")

    print(f"Experiment results saved as {filename}")

def saveExperimentFolder(agent, experiment, phase, agentStats, gameProperties):
    global directory

    if isinstance(agent, AgentQ):
        agentTypeDirectory = "Q"

    elif isinstance(agent, AgentDQN):
        agentTypeDirectory = "DQN"

    ##Store the folder in the correct location (Depending on Q/DQN)
    agentFolder = os.path.join(directory, agentTypeDirectory, f"experiment_{experiment}")
    os.makedirs(agentFolder, exist_ok=True)

    writeFile(agentFolder, f"experiment_{experiment}_agent_{agent.playerID}.txt", agentStats['total'], agent.lrParameters, gameProperties, agent)
    writeFile(agentFolder, f"phase_{phase}_agent_{agent.playerID}.txt", agentStats['phase'], agent.lrParameters, gameProperties, agent)

    ##Plot the survival rates for both the phase and total training
    plotSurvivalRate(agentStats['total'], intervals, experiment, agentFolder)
    plotSurvivalRate(agentStats['phase'], intervals, experiment, agentFolder, phase)

    ##Plot the average reward over time
    plotAverageRewards(agentStats['total'], intervals, experiment, agentFolder)
    plotAverageRewards(agentStats['phase'], intervals, experiment, agentFolder, phase)

    ##Plot average game lengths
    plotAverageGameLength(agentStats['total'], intervals, experiment, agentFolder)
    plotAverageGameLength(agentStats['phase'], intervals, experiment, agentFolder, phase)
    
    ##Save Metadata
    saveMetadata(agentStats['total'], agentFolder, experiment = experiment)
    saveMetadata(agentStats['phase'], agentFolder, phase = phase)

    ##Save the Q-Table
    if isinstance(agent, AgentQ):
        saveQTable(agent.qTable, agentFolder, experiment)

    elif isinstance(agent, AgentDQN):
        saveModel(agent.model, agentFolder, experiment)
        saveReplayBuffer(agent.replayBuffer, agentFolder, experiment)

def agentTraining(playerTypes, gameProperties, intervals, trainingIterations):
    playerList, metadataList = createPlayers(playerTypes, True)
    playerList, agentsStats = runExperiment(playerList, metadataList, gameProperties, intervals, trainingIterations)

    for i, (player, stats) in enumerate(zip(playerList, agentsStats)):
        if isinstance(player, Agent):
            config = playerTypes[i]
            
            if isinstance(config, dict):
                experiment = config['experiment']
                phase = config['phase']

            else:
                print("Error. Not finding correct config file")
        
            saveExperimentFolder(player, experiment, phase, stats, gameProperties)

intervals = 1000
trainingIterations = 50000

##RL Agent parameters
lrParams = {
    "learningRate": 0.1,
    "discount": 0.99,
    "epsilon": 0.1,
    "gamma" : 0,
    "batchSize" : 128,
    "inputSize" : 1062,
    "outputSize" : 174,
    "learningIntervals" : 1000,
    "bufferCapacity" : 1000000,
    "trainingIterations" : 200
}

gameProperties = {
    "handCount" : 6,
    "talonCount" : 24,
    "printGameplay" : False
}

##Results are stored in experiments folder
directory = os.path.abspath(os.path.join(os.getcwd(), 'experiments'))

##Player Types Are:
    ## Human            - 0
    ## RandomBot        - 1
    ## LowestValueBot   - 2
    ## Q Agent          - 3
    ## DQN Agent        - 4
playerTypes = [
    1, 
    {"type" : 4, "experiment" : "1", "phase" : "Rand_Bot", 'parameters': lrParams}
]

##{"type" : 4, "experiment" : "1", "phase" : "A", 'parameters': lrParams},


##Phase Codes:
## A - 2P RandomBot Training
## B - 2P LowestValueBot Training
## C - 3 Player Matches

agentTraining(playerTypes, gameProperties, intervals, trainingIterations)

##playGame([2, 2], gameProperties)