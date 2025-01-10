from colorama import Fore
import time
import secrets
from random import randint, uniform
import os
import sys
import select
import tty
import termios
import signal
import re

ascii_art = f"""
{Fore.CYAN}
██╗  ██╗███╗   ███╗██╗███╗   ██╗███████╗
╚██╗██╔╝████╗ ████║██║████╗  ██║██╔════╝
 ╚███╔╝ ██╔████╔██║██║██╔██╗ ██║█████╗  
 ██╔╝██╗██║╚██╔╝██║██║██║╚██╗██║██╔══╝  
██╔╝ ██╗██║ ╚═╝ ██║██║██║ ╚████║███████╗
╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝
                 {Fore.YELLOW}v2.1
{Fore.RESET}
"""

print(ascii_art)

continuing = False
balance = 0.0
btcval = 82253.44
wallet_address = ""
start_time = 0
total_addresses_mined = 0
successful_addresses = []

balance_file = "balance.txt"
if os.path.exists(balance_file):
    with open(balance_file, "r") as f:
        balance = float(f.read())

print("> 1 to Start or 2 to Exit?")
answer = input("> ").lower()

if answer == "1":
    print("Please enter your wallet address to receive mined Bitcoin:")
    wallet_address = input("> ").strip()
    if not re.match(r"^(bc1[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{25,39}|1[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{25,39})$", wallet_address):
        try:
            int(wallet_address)
        except ValueError:
            print(f"Invalid wallet address: {wallet_address}")
            exit()
    print(f"Wallet address {wallet_address} saved.")
    print("Starting in 3")
    time.sleep(1)
    print("Starting in 2")
    time.sleep(1)
    print("Starting in 1")
    time.sleep(0.8)
    print("Starting..")
    time.sleep(0.5)
    print("Starting...")
    continuing = True
    start_time = time.time()

elif answer == "2":
    print("Exiting..")
    exit()

def is_ctrl_x_pressed():
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

def handle_exit_signal(signum, frame):
    global continuing
    continuing = False

signal.signal(signal.SIGINT, handle_exit_signal)
signal.signal(signal.SIGTERM, handle_exit_signal)

def generate_btc_address():
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    return "1" + ''.join(secrets.choice(alphabet) for _ in range(33))

def simulate_block_solving():
            """ Simulate the solving of a block with a delay and reward the miner with BTC. """
            print(Fore.CYAN + "A block has been found! Solving it..." + Fore.RESET)
            time.sleep(5)  # Simulate time taken to solve the block

            # Random chance that someone else might mine the block
            if randint(1, 10) <= 2:  # 20% chance someone else mines it first
                print(Fore.RED + "Block mining unsuccessful. Continuing..." + Fore.RESET)
            else:
                # If block is successfully mined
                block_reward = 6.25  # Current Bitcoin block reward
                transaction_fees = round(uniform(0.1, 2.0), 6)  # Simulate transaction fees
                total_reward = block_reward + transaction_fees

                # Add reward to balance
                global balance
                balance += total_reward

                # Display block solved and reward
                print(Fore.GREEN + f"Block solved! {total_reward:.6f} BTC (£{total_reward * btcval:.2f})" + Fore.RESET)
                time.sleep(3)


session_btc_earned = 0.0
try:
    while continuing:
        time.sleep(0.01)  # Simulating ongoing mining activity
        total_addresses_mined += 1

        # 1 in 500,000 chance to find a block
        if randint(1, 1000000) == 1:
            simulate_block_solving()

        # Simulating generating BTC addresses
        mined_wallet = generate_btc_address()
        print(Fore.WHITE + f"> {mined_wallet}" + Fore.RED + " > 0.000000 BTC ($0.00)")

        # Check if Ctrl+X is pressed to exit mining
        if is_ctrl_x_pressed():
            print("Exiting mining session...")
            continuing = False

finally:
    with open(balance_file, "w") as f:
        f.write(f"{balance:.6f}")
    session_money_earned = round(btcval * session_btc_earned, 2)
    runtime = round(time.time() - start_time, 2)
    success_rate = (len(successful_addresses) / total_addresses_mined) * 100
    print("\nYour final balance: " + Fore.GREEN + f"{balance:.6f} BTC (£" + str("{:,}".format(round(btcval * balance, 2))) + ")")
    print("This session: " + Fore.GREEN + f"{session_btc_earned:.6f} BTC (£" + str("{:,}".format(session_money_earned)) + ")")
    print(f"Total IPs mined: {Fore.YELLOW}{total_addresses_mined}")
    print(f"Session runtime: {Fore.YELLOW}{runtime} seconds{Fore.RESET}")
    print(f"Successful Addresses: {Fore.YELLOW}{len(successful_addresses)}")
    print(f"Success Rate: {Fore.YELLOW}{success_rate:.2f}%{Fore.RESET}")
