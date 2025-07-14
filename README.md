# 🚗 Car NEAT-AI Simulator

This is a 2D AI simulation where **Car vehicles** are autonomously controlled by evolving neural networks using the **NEAT (NeuroEvolution of Augmenting Topologies)** algorithm. The goal is for the cars to learn how to avoid dynamic obstacles and survive as long as possible while maintaining optimal movement.

---

## 🎮 Game Overview

Each Honda car is controlled by a neural network. Through evolution over generations, the networks learn:
- Obstacle avoidance,
- Lane-centering behavior,
- Survival in increasingly difficult conditions,
- Smooth and strategic movement.

---

## 🧠 AI & Fitness Strategy

Each genome (neural network) is rewarded or penalized based on:

| Metric                        | Description                                               |
|------------------------------|-----------------------------------------------------------|
| ✅ Distance traveled          | Longer survival yields higher fitness                    |
| ✅ Lane centering             | Staying close to the road center is rewarded             |
| ✅ Object avoidance           | Avoiding obstacles without collision yields bonus        |
| ❌ Collisions                 | Result in immediate and scaled penalties                 |
| ❌ Erratic movement           | Rapid up/down movement is penalized                      |
| ✅ Handling dense traffic     | Surviving under heavy object density earns rewards       |

All results are logged to `results.csv` and `generation_stats.csv`.

## 🛠️ TODO

- [ ] 🎞️ **Add background and car movement animation**
  - Ensure the background moves smoothly to simulate road motion.
  - Animate cars and objects realistically — possibly add lane markers scrolling, shadowing, or motion blur.
  - Synchronize object movement with game speed for consistent visual feedback.
  - Make sure animation speed scales properly with global speed.

- [ ] 🧠 **Improve AI decision-making**
  - Refine reward functions for better lane discipline and collision avoidance.
  - Penalize erratic or oscillatory movement.
  - Encourage long-term survival and smoother control.


- [ ] 🚧 **Prevent overlapping of obstacle cars**
  - Add logic to ensure obstacle cars (those to be avoided) do not spawn too close to each other.
  - Detect proximity at spawn and adjust position or skip spawn to maintain spacing.
  - This avoids impossible paths and makes gameplay fairer and more realistic.

