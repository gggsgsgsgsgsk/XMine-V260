# Bitcoin Mining Simulator

A simple Bitcoin mining simulator written in Python. This script mimics the process of mining by generating pseudo-random Bitcoin addresses, simulating share rewards, and occasionally "mining" a block. While it uses Bitcoin (BTC) terminology and reward values by default, the code is fully customizable and can be adapted for other cryptocurrencies or for simulating other reward systems.

## Features

- **Simulated Mining:** Generates random Bitcoin addresses and simulates the mining process.
- **Reward Simulation:** Simulates share rewards (small, medium, and big) and block rewards with transaction fees.
- **Customizable Configuration:** Easily adjust probabilities, reward ranges, sleep times, and other parameters to suit your needs.
- **Real-Time Feedback:** Displays colored output in the terminal showing mining events and rewards.
- **Session Statistics:** On exit (using Ctrl+X or Ctrl+C), the script prints session statistics, including total rewards, runtime, and more.
- **Wallet Input Validation:** Prompts the user to enter a Bitcoin wallet address with basic validation before starting the mining simulation.

## Customization Options

The simulation parameters are defined in a configuration dictionary at the beginning of the script. You can change these values to adjust the simulation's behavior:

- **SLEEP_TIME:** Delay between each iteration (simulating work time).
- **BLOCK_MINING_PROB_DENOMINATOR:** Controls the probability of a block event (e.g., 1 in 1,200,000 iterations).
- **SELF_MINING_PROBABILITY:** Chance that the simulated miner is the one who mines the block.
- **SHARE_PROB_DENOMINATOR:** Frequency of share submissions.
- **Reward Ranges:** The script provides different reward tiers:
  - **NORMAL_REWARD_MIN/MAX:** For normal share rewards (default: 1–5 satoshis).
  - **MEDIUM_SHARE_REWARD_MIN/MAX:** For medium share rewards.
  - **BIG_SHARE_REWARD_MIN/MAX:** For big share rewards.
- **BLOCK_REWARD and TX_FEES_MIN/MAX:** The block reward and transaction fees.
- **BTCVAL:** The fiat conversion value for Bitcoin (used for display purposes).
- **Pause Times:** Delays after awarding medium/big shares and after mining a block.

**Note:** Although the default parameters are set with Bitcoin values in mind, you can easily modify the configuration to simulate other cryptocurrencies or adjust the probabilities and rewards to create a more or less realistic mining simulation.

## How Realistic Is It?

This simulator uses probabilistic methods to mimic the mining process:
- **Block Mining:** The chance of mining a block is low (e.g., roughly one block every 1,200,000 iterations), similar to the difficulty of mining real blocks.
- **Share Rewards:** The different share rewards (small, medium, big) are randomly determined, simulating the variability seen in mining pools.
- **Customizability:** While the simulation is not a real mining process, the parameters allow you to adjust realism and complexity to your taste.

Keep in mind, this script is for educational and entertainment purposes only. It does not perform any actual mining on any blockchain network.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/gggsgsgsgsk/bitcoin-mining-simulator.git
   cd bitcoin-mining-simulator

2. **Install the required Python packages:**

   ```bash
   pip install colorama

## Usage

**Run the script:**

   ```bash
   python3 mining_sim.py

all credits to me
