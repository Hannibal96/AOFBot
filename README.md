# ♠️ PokerBot — Deep Learning Poker Agent

**PokerBot** is an intelligent poker-playing agent built in **Python** that combines **computer vision** and **reinforcement learning** to make strategically strong, game-theoretic decisions.

---

## 🎬 Project Demo
[![AOFBot live recording](https://img.youtube.com/vi/skpdq-eVWLA/0.jpg)](https://www.youtube.com/watch?v=skpdq-eVWLA)
[![Watch the demo](https://img.youtube.com/vi/skpdq-eVWLA/maxresdefault.jpg)](https://www.youtube.com/watch?v=skpdq-eVWLA)

👉 Full video walkthrough: https://www.youtube.com/watch?v=skpdq-eVWLA

---

## 🧠 How It Works

PokerBot operates in two main stages: **game state recognition** and **strategy optimization**.

### 🎯 1. Game State Recognition (CNN)

A **Convolutional Neural Network (CNN)** analyzes the visual state of the poker table and extracts structured information, including:

- Player hole cards  
- Community cards  
- Pot size  
- Player stack sizes  
- Betting actions  

This allows the bot to transform raw visual input into a machine-readable poker game state.

---

### ♟️ 2. Strategy Learning (Reinforcement Learning + C++ Simulator)

After identifying the game state, PokerBot selects actions using a **reinforcement learning (RL)** agent trained through large-scale self-play.

Training and equilibrium approximation are powered by a high-performance **C++ poker simulator**:

https://github.com/Hannibal96/poker_simulator

This simulator enables:

- Fast large-scale simulations  
- Self-play training  
- Approximation of game-theoretic equilibrium strategies  

By learning in an equilibrium-focused environment, PokerBot develops strategies that are **robust**, **adaptive**, and difficult for opponents to exploit.

---

## 🚀 Key Features

- 🎥 **Vision-based gameplay** — understands the table directly from visual input  
- 🧠 **CNN-powered state detection** — converts images into structured poker states  
- 🎯 **Reinforcement learning decision engine** — learns optimal play through simulation  
- ♟️ **Game-theory driven** — strategies derived from equilibrium-style training  
- ⚡ **Hybrid Python + C++ architecture** for both flexibility and performance  

---

## 🧩 Tech Stack

- **Python** — Bot logic and neural networks  
- **Convolutional Neural Networks (CNNs)** — Game state recognition  
- **Reinforcement Learning (RL)** — Strategy optimization  
- **C++ Poker Simulator** — High-speed environment for training and equilibrium computation  

---

PokerBot blends **computer vision**, **deep reinforcement learning**, and **game theory** to create a competitive poker AI capable of making principled decisions in complex, uncertain environments.
