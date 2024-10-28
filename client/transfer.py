import argparse
import logging
from client import *

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

def transfer(wallet_name, dest_wallet, transfer):
    main_keyfile = f'/root/.sawtooth/keys/{wallet_name}.priv'
    dest_keyfile = f'/root/.sawtooth/keys/{dest_wallet}.priv'
    client = SimpleWalletClient(baseUrl='http://rest-api:8008', keyFile=main_keyfile)
    client2 = SimpleWalletClient(baseUrl='http://rest-api:8008', keyFile=dest_keyfile)
    LOGGER.info(f"Transfer money from {wallet_name} to {dest_wallet}")
    client.transfer(transfer, dest_keyfile)

def main():
    parser = argparse.ArgumentParser(description='Trasfer')
    parser.add_argument('-r', '--swallet', type=str, required=True, help='Name of the source wallet')
    parser.add_argument('-d', '--dwallet', type=str, required=True, help='Name of the destination wallet')
    parser.add_argument('-p', '--value', type = int, nargs='+', required=True, help='Money to transfer')
    args = parser.parse_args()
    transfer(args.swallet, args.dwallet, args.value)

if __name__ == '__main__':
    main()
