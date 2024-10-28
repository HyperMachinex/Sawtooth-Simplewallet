from client import *
import argparse
import logging

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def create_wallet(name):
    keyfile = f'/root/.sawtooth/keys/{name}.priv'
    client = SimpleWalletClient(baseUrl='http://rest-api:8008', keyFile=keyfile)
    LOGGER.info(f"Creating wallet: {name}")

def main():
    parser = argparse.ArgumentParser(description='Create a wallet')
    parser.add_argument('wallet_name', type=str, help='Name of the wallet')
    args = parser.parse_args()
    create_wallet(args.wallet_name)

if __name__ == '__main__':
    main()
