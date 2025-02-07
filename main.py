#!/usr/bin/env python3
from colorama import Fore, init
import time
import secrets
from random import randint, uniform, random
import os
import sys
import signal
import re
import atexit

# Run using this command (when in the same directory):
#   python3 mining_sim.py

# IMPORTANT: use ctrl+x to exit, or ctrl+c if not working.

init(autoreset=True)

# ================= Configuration ==================
# Adjust these settings as needed:
CONFIG = {
    "SLEEP_TIME": 0.05,                      # seconds per iteration (simulate work time)
    "BLOCK_MINING_PROB_DENOMINATOR": 1200000,  # ~1 block every 1,200,000 iterations (realistic chance)
    "SELF_MINING_PROBABILITY": 20,            # probability that YOU mine the block (else, someone else does)
    # Set the share event to occur 1 in 1000 iterations (rarer than before)
    "SHARE_PROB_DENOMINATOR": 1000,           

    "NORMAL_REWARD_MIN": 0.00000001,           # Lower bound for normal share reward in BTC (1 satoshi)
    "NORMAL_REWARD_MAX": 0.0000005,            # Upper bound for normal share reward in BTC

    # Make medium share rewards rarer: 1 in 2000 chance among share events
    "MEDIUM_SHARE_PROB_DENOMINATOR": 2000,     
    "MEDIUM_SHARE_REWARD_MIN": 0.000001,       # Lower bound for medium share reward in BTC (~100 satoshis)
    "MEDIUM_SHARE_REWARD_MAX": 0.0005,         # Upper bound for medium share reward in BTC (~500 satoshis)

    # Big share rewards now occur 1 in 5000 share events
    "BIG_SHARE_PROB_DENOMINATOR": 5000,        
    "BIG_SHARE_REWARD_MIN": 0.001,             # Lower bound for big share reward in BTC
    "BIG_SHARE_REWARD_MAX": 0.008,             # Upper bound for big share reward in BTC

    # New "Really Big Reward": 1 in 50000 share events
    "REALLY_BIG_SHARE_PROB_DENOMINATOR": 50000, 
    "REALLY_BIG_SHARE_REWARD_MIN": 0.001,      # Lower bound for really big reward in BTC
    "REALLY_BIG_SHARE_REWARD_MAX": 0.5,        # Upper bound for really big reward in BTC

    "BLOCK_REWARD": 6.25,                      # Block reward in BTC
    "TX_FEES_MIN": 0.0,                        # Minimum transaction fees (BTC)
    "TX_FEES_MAX": 0.5,                        # Maximum transaction fees (BTC)
    "BTCVAL": 79278.80,                        # BTC fiat conversion value (e.g., in pounds)
    "PAUSE_TIME_SHARE": 1,                     # pause (in seconds) when a medium, big, or really big share is awarded
    "PAUSE_TIME_BLOCK": 2,                     # pause (in seconds) after a block is solved
}

letters = {
    "X": [
        "██╗  ██╗",
        "╚██╗██╔╝",
        " ╚███╔╝ ",
        " ██╔██╗ ",
        "██╔╝ ██╗",
        "╚═╝  ╚═╝",
    ],
    "M": [
        "███╗   ███╗",
        "████╗ ████║",
        "██╔████╔██║",
        "██║╚██╔╝██║",
        "██║ ╚═╝ ██║",
        "╚═╝     ╚═╝"
    ],
    "I": [
        "██╗",
        "██║",
        "██║",
        "██║",
        "██║",
        "╚═╝"
    ],
    "N": [
        "███╗   ██╗",
        "████╗  ██║",
        "██╔██╗ ██║",
        "██║╚██╗██║",
        "██║ ╚████║",
        "╚═╝  ╚═══╝"
    ],
    "E": [
        "███████╗",
        "██╔════╝",
        "█████╗  ",
        "██╔══╝  ",
        "███████╗",
        "╚══════╝"
    ]
}

gradient = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]

for i in range(6):
    line = (letters["X"][i] + "   " +
            letters["M"][i] + "   " +
            letters["I"][i] + "   " +
            letters["N"][i] + "   " +
            letters["E"][i])
    print(gradient[i] + line)
print(f"{Fore.YELLOW}v2.6.0 RELEASE\n{Fore.RESET}")

# ================= Global Variables ====================
continuing = False
balance = 0.00
btcval = CONFIG["BTCVAL"]
wallet_address = ""
start_time = 0
total_addresses_mined = 0
successful_addresses = []
session_btc_earned = 0.00

# Counters for shares and blocks
small_shares_count = 0
medium_shares_count = 0
big_shares_count = 0
really_big_shares_count = 0
blocks_count = 0
other_blocks_count = 0

balance_file = "balance.txt"
if os.path.exists(balance_file):
    with open(balance_file, "r") as f:
        try:
            balance = float(f.read())
        except ValueError:
            balance = 0.00

print("> 1 to Start or 2 to Exit?")
answer = input("> ").lower()

if answer == "1":
    print("Please enter your wallet address to receive mined Bitcoin:")
    wallet_address = input("> ").strip()
    # Modified regex: Added '-' to allow dashes in the wallet address
    if not re.match(r"^(bc1[-qpzry9x8gf2tvdw0s3jn54khce6mua7l]{25,39}|1[-123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{25,39})$", wallet_address):
        try:
            int(wallet_address)
        except ValueError:
            print(f"Invalid wallet address: {wallet_address}")
            exit()
    print(f"Wallet address {wallet_address} saved.")
    for i in range(3, 0, -1):
        print(f"Starting in {i}...")
        time.sleep(1)
    print("Starting...")
    continuing = True
    start_time = time.time()
    print("Press Ctrl+X or Ctrl+C to exit and see your session stats.")
elif answer == "2":
    print("Exiting...")
    exit()

# ================= Helper Functions =====================
def is_ctrl_x_pressed():
    """
    Cross-platform check for Ctrl+X.
    On Windows, uses msvcrt.
    On Unix-like systems, uses termios and select.
    """
    try:
        if os.name == 'nt':
            import msvcrt
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                if ch == b'\x18':  # Ctrl+X
                    return True
        else:
            import select, tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                dr, _, _ = select.select([sys.stdin], [], [], 0)
                if dr:
                    key = sys.stdin.read(1)
                    if key == '\x18':
                        return True
                return False
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except Exception:
        return False

def handle_exit_signal(signum, frame):
    global continuing
    continuing = False

signal.signal(signal.SIGINT, handle_exit_signal)
signal.signal(signal.SIGTERM, handle_exit_signal)

def generate_btc_address():
    """Generate a pseudo-random Bitcoin address."""
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    return "1" + ''.join(secrets.choice(alphabet) for _ in range(33))

def simulate_block_solving():
    global balance, session_btc_earned, blocks_count, other_blocks_count
    print(Fore.CYAN + "\nA block event occurred!" + Fore.RESET)
    time.sleep(5)
    if random() < CONFIG["SELF_MINING_PROBABILITY"]:
        tx_fees = round(uniform(CONFIG["TX_FEES_MIN"], CONFIG["TX_FEES_MAX"]), 8)
        total_reward = CONFIG["BLOCK_REWARD"] + tx_fees
        balance += total_reward
        session_btc_earned += total_reward
        blocks_count += 1
        print(Fore.GREEN + f"Congratulations! You mined a block!\n"
              f"Block Reward: {CONFIG['BLOCK_REWARD']} BTC, Transaction Fees: {tx_fees} BTC, "
              f"Total: {total_reward:.8f} BTC (£{total_reward * btcval:.2f})" + Fore.RESET)
    else:
        other_blocks_count += 1
        print(Fore.RED + "Someone else has mined the block. No rewards for you." + Fore.RESET)
    time.sleep(CONFIG["PAUSE_TIME_BLOCK"])

def print_stats():
    session_money_earned = round(btcval * session_btc_earned, 2)
    runtime = round(time.time() - start_time, 2)
    success_rate = (len(successful_addresses) / total_addresses_mined) * 100 if total_addresses_mined > 0 else 0
    print("\nYour final balance: " + Fore.GREEN + f"{balance:.8f} BTC (£{round(btcval * balance, 2):,})")
    print("This session: " + Fore.GREEN + f"{session_btc_earned:.8f} BTC (£{session_money_earned:,})")
    print(f"Total work units processed: {Fore.YELLOW}{total_addresses_mined}")
    print(f"Session runtime: {Fore.YELLOW}{runtime} seconds{Fore.RESET}")
    print(f"Successful rewards (shares + blocks): {Fore.YELLOW}{len(successful_addresses)}")
    print(f"Success Rate: {Fore.YELLOW}{success_rate:.4f}%{Fore.RESET}")
    print(f"Small Share Rewards: {Fore.YELLOW}{small_shares_count}{Fore.RESET}")
    print(f"Medium Share Rewards: {Fore.YELLOW}{medium_shares_count}{Fore.RESET}")
    print(f"Big Share Rewards: {Fore.YELLOW}{big_shares_count}{Fore.RESET}")
    print(f"Really Big Share Rewards: {Fore.YELLOW}{really_big_shares_count}{Fore.RESET}")
    print(f"Blocks Mined by You: {Fore.YELLOW}{blocks_count}{Fore.RESET}")
    print(f"Blocks Mined by Others: {Fore.YELLOW}{other_blocks_count}{Fore.RESET}")
atexit.register(print_stats)

# ================= Main Mining Loop =====================
try:
    while continuing:
        total_addresses_mined += 1
        time.sleep(CONFIG["SLEEP_TIME"])
        if randint(1, CONFIG["SHARE_PROB_DENOMINATOR"]) == 1:
            # Check for Really Big Reward first (rarest event)
            if randint(1, CONFIG["REALLY_BIG_SHARE_PROB_DENOMINATOR"]) == 1:
                reward = round(uniform(CONFIG["REALLY_BIG_SHARE_REWARD_MIN"], CONFIG["REALLY_BIG_SHARE_REWARD_MAX"]), 8)
                reward_type = "Really Big Reward"
                really_big_shares_count += 1
            # Then check for a Big Share Reward
            elif randint(1, CONFIG["BIG_SHARE_PROB_DENOMINATOR"]) == 1:
                reward = round(uniform(CONFIG["BIG_SHARE_REWARD_MIN"], CONFIG["BIG_SHARE_REWARD_MAX"]), 8)
                reward_type = "Big Share Reward"
                big_shares_count += 1
            # Then check for a Medium Share Reward
            elif randint(1, CONFIG["MEDIUM_SHARE_PROB_DENOMINATOR"]) == 1:
                reward = round(uniform(CONFIG["MEDIUM_SHARE_REWARD_MIN"], CONFIG["MEDIUM_SHARE_REWARD_MAX"]), 8)
                reward_type = "Medium Share Reward"
                medium_shares_count += 1
            else:
                reward = round(uniform(CONFIG["NORMAL_REWARD_MIN"], CONFIG["NORMAL_REWARD_MAX"]), 8)
                reward_type = "Share Reward"
                small_shares_count += 1
            balance += reward
            session_btc_earned += reward
            mined_wallet = generate_btc_address()
            print(Fore.WHITE + f"> {mined_wallet}" + Fore.GREEN +
                  f" > {reward_type}: {reward:.8f} BTC (£{round(btcval * reward, 2):,})")
            successful_addresses.append(mined_wallet)
            if reward_type in ["Medium Share Reward", "Big Share Reward", "Really Big Reward"]:
                time.sleep(CONFIG["PAUSE_TIME_SHARE"])
        else:
            mined_wallet = generate_btc_address()
            print(Fore.WHITE + f"> {mined_wallet}" + Fore.RED + " > 0.00000000 BTC (£0.00)")

        if randint(1, CONFIG["BLOCK_MINING_PROB_DENOMINATOR"]) == 1:
            simulate_block_solving()

        if is_ctrl_x_pressed():
            print("Exiting mining session...")
            continuing = False

except KeyboardInterrupt:
    print("KeyboardInterrupt received. Exiting mining session...")

finally:
    with open(balance_file, "w") as f:
        f.write(f"{balance:.8f}")
