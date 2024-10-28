from client import *
import argparse
import logging

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def balance(wallet_name):
    keyfile = f'/root/.sawtooth/keys/{wallet_name}.priv'
    client = SimpleWalletClient(baseUrl='http://rest-api:8008', keyFile=keyfile)
    LOGGER.info(f"Balance checking: {wallet_name}")
    balance = client.balance()
    LOGGER.info(f"Balance: {balance}")

def main():
    parser = argparse.ArgumentParser(description='Show balance')
    parser.add_argument('wallet_name', type=str, help='Name of the wallet')
    args = parser.parse_args()
    balance(args.wallet_name)

if __name__ == '__main__':
    main()
