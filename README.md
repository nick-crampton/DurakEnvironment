# Durak RL: Reinforcement Learning Agents for Durak</h1>
This project explores the application of Reinforcement Learning (RL) to the strategic card game Durak. It uses Q-Learning and Deep Q-Networks (DQN) to train AI agents capable of playing the game at a high strategic level.

### About the Project
Durak is a complex, multi-stage card game involving attack-defense interactions. This project aims to train agents capable of playing Durak by leveraging RL methods, primarily Q-Learning and DQN.

### Key objectives:

- Simulate Durak using a Python-based environment.
- Train and evaluate RL agents against both heuristic-based bots and random action bots.
- Compare the effectiveness of Q-Learning vs. DQN for strategic decision-making in Durak.

## Environment Design

The Durak environment is designed to emulate the full game, including:
- **Card transactions**: Drawing, attacking, defending, and talon management.
- **Attack and defense logic**: Players alternate roles, with a goal of shedding cards.
- **Game mechanics**: Role assignment, player turns, and game outcomes.
- **Game components**: Six core classes (`Card`, `Deck`, `Player`, `Round`, `Game`, `GameState`).

Bots included:
- **RandomBot**: A bot that takes random legal actions.
- **LowestValueBot**: A heuristic bot that plays the lowest-value card available.

## RL Approaches

### Q-Learning Agent
- Uses a tabular approach to learn the optimal strategy by exploring and exploiting game states.
- Demonstrates strong long-term planning and tactical awareness.

### DQN Agent
- Implements a neural network-based RL method to approximate Q-values.
- Faces challenges in state space complexity and action masking.

## Results

The Q-Learning agent consistently outperforms both RandomBot and LowestValueBot, showing high survival rates and advanced strategic planning. The DQN agent, while effective in some cases, struggles with convergence due to the complexity of the state space.

## Paper

You can read the full paper [here](./llhl72Project.pdf).

