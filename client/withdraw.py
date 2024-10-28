import argparse
import logging
from client import *

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

def withdraw(wallet_name, withdraw):
    keyfile = f'/root/.sawtooth/keys/{wallet_name}.priv'
    client = SimpleWalletClient(baseUrl='http://rest-api:8008', keyFile=keyfile)
    LOGGER.info(f"Withdraw money from {wallet_name}: {withdraw}")
    client.withdraw(withdraw)

def main():
    parser = argparse.ArgumentParser(description='Withdraw')
    parser.add_argument('-r', '--wallet', type=str, required=True, help='Name of the wallet')
    parser.add_argument('-p', '--value', type = int, nargs='+', required=True, help='Money to withdraw')
    args = parser.parse_args()
    withdraw(args.wallet, args.value)

if __name__ == '__main__':
    main()
