from durakNew.playerTypes.agentQ import AgentQ
from durakNew.playerTypes.DQN.agentDQN import AgentDQN
from durakNew.playerTypes.DQN.replayBuffer import ReplayBuffer
from durakNew.playerTypes.randomBot import RandomBot
from durakNew.playerTypes.humanPlayer import HumanPlayer
from durakNew.playerTypes.lowestValueBot import LowestValueBot

from durakNew.game import Game
import os
import json

##Creates player, loads agent's q-tables, and models to load previous progress.
def createPlayers(playerTypes, lrParams, training = True, qTable = None, replayBuffer = None, model = None):
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
            newPlayer = AgentQ([], i, None, learningRate = lrParams["learningRate"], discount = lrParams["discount"], epsilon = lrParams["epsilon"], qTable = qTable, isTraining = training)
            pass

        elif playerType == 4:
            ##Create DQN Agent
            newPlayer = AgentDQN([], i, None, learningRate = lrParams["learningRate"], discount = lrParams["discount"], epsilon = lrParams["epsilon"], gamma = lrParams["gamma"], model = model,  replayBuffer = replayBuffer)

        playerList.append(newPlayer)

    return playerList

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

def loadMetadata(directory, experiment):
    metadataDirectory = os.path.join(directory, 'Metadata')
    filepath = os.path.join(metadataDirectory, f'Metadata_experiment_{experiment}')

    if not os.path.exists(filepath):
        print(f"No metadata found at {filepath}")
        return None
    
    with open(filepath, 'r') as file:
        metadata = json.load(file)

    return metadata

def playGame(playerList, gameProperties):
    game = Game(playerList, gameProperties = gameProperties)
    game.newGame()

def loadProgress(playerTypes, modelNames):
    
    for playerType in playerTypes:
        ##If player is an agent of some sort, load their progress if there is any
        if playerType in [3, 4]:
            if playerType == 3:
                for key in modelNames:
                    if key == 3:
                        qName = modelNames.get(key)
                        qTable, metadata = fetchQProgress(qName)
                        modelNames.pop(key)

                        


                        
def fetchQProgress(qName):
    experimentFolder = f"experiment_{qName}"
    folderPath = os.path.join(directory, experimentFolder)

    qTable = loadJSON(folderPath, qName)
    metadata = loadMetadata(folderPath, qName)

    return qTable, metadata
    

        
def fetchDQNProgress()


    


##Results are stored in experiments folder
directory = os.path.abspath(os.path.join(os.getcwd(), 'experiments'))

##Player Types Are:
    ## Human            - 0
    ## RandomBot        - 1
    ## LowestValueBot   - 2
    ## Q Agent          - 3
    ## DQN Agent        - 4
playerTypes = [2, 3]

