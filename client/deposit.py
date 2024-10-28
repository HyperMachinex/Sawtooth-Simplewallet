import argparse
import logging
from client import *

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

def deposit(wallet_name, deposit):
    keyfile = f'/root/.sawtooth/keys/{wallet_name}.priv'
    client = SimpleWalletClient(baseUrl='http://rest-api:8008', keyFile=keyfile)
    LOGGER.info(f"Deposit money to {wallet_name}: {deposit}")
    client.deposit(deposit)

def main():
    parser = argparse.ArgumentParser(description='Deposit')
    parser.add_argument('-r', '--wallet', type=str, required=True, help='Name of the wallet')
    parser.add_argument('-p', '--value', type = int, nargs='+', required=True, help='Money to deposit')
    args = parser.parse_args()
    deposit(args.wallet, args.value)

if __name__ == '__main__':
    main()
