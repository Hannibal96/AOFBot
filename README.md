# ♠️ PokerBot — Deep Learning Poker Agent

**PokerBot** is an intelligent poker-playing agent written in **Python** that combines **computer vision**, **reinforcement learning**, and **game theory** to make strategically optimal decisions.

The bot observes the poker table visually, reconstructs the full game state using deep learning, and selects actions based on strategies learned from equilibrium-focused self-play.

---

## 🎬 Demo

[![Watch the demo](https://img.youtube.com/vi/skpdq-eVWLA/maxresdefault.jpg)](https://www.youtube.com/watch?v=skpdq-eVWLA)

---

## 🧠 How It Works

PokerBot operates in two main stages:

### 🎯 1. Game State Identification (CNN)

A **Convolutional Neural Network (CNN)** processes the visual representation of the poker table and extracts a structured game state, including:

- Player hole cards  
- Community cards  
- Pot size  
- Stack sizes  
- Betting actions and round information  

This allows the agent to interact with the game using raw visual input rather than predefined state variables.

---

### ♟️ 2. Strategy Learning via Reinforcement Learning

Once the game state is identified, the bot selects actions using a **reinforcement learning (RL)** policy trained through large-scale self-play.

Training and equilibrium computation are performed using a high-performance C++ poker environment:

**:contentReference[oaicite:0]{index=0}**

This simulator enables:

- Fast and scalable self-play  
- Approximation of game-theoretic equilibria  
- Learning robust, low-exploitability strategies  

By training against an equilibrium-seeking environment, PokerBot develops principled strategies that generalize well across different opponents.

---

## 🚀 Key Features

- Vision-based poker gameplay  
- CNN-driven state reconstruction  
- Reinforcement learning decision engine  
- Game-theoretic, equilibrium-focused strategy learning  
- Hybrid **Python + C++** architecture for flexibility and performance  

---

## 🧩 Tech Stack

- **Python** — Bot logic and neural networks  
- **Convolutional Neural Networks (CNNs)** — State identification  
- **Reinforcement Learning (RL)** — Strategy optimization  
- **C++ Poker Simulator** — High-speed training and equilibrium computation  

---

PokerBot integrates **deep learning**, **reinforcement learning**, and **game theory** to create a competitive poker AI capable of making strong decisions in complex, imperfect-information environments.
