import base64
import random
import requests
import yaml
import hashlib
from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader, Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchList, BatchHeader, Batch

FAMILY_NAME = 'simplewallet'

def _hash(data):
    return hashlib.sha512(data).hexdigest()

class SimpleWalletClient(object):

    def __init__(self, baseUrl, keyFile=None):
        self._baseUrl = baseUrl
        if keyFile is None:
            self._signer = None
            return

        self._load_key(keyFile)

        self._address = _hash(FAMILY_NAME.encode('utf-8'))[0:6] + \
                        _hash(self._publicKey.encode('utf-8'))[0:64]


    # provate key
    def _load_key(self, keyFile):
        try:
            with open(keyFile) as fd:
                privateKeyStr = fd.read().strip()
        except OSError as err:
            raise Exception(f'Failed to read private key {keyFile}: {str(err)}')

        try:
            privateKey = Secp256k1PrivateKey.from_hex(privateKeyStr)
        except ParseError as err:
            raise Exception(f'Failed to load private key: {str(err)}')

        self._signer = CryptoFactory(create_context('secp256k1')).new_signer(privateKey)
        self._publicKey = self._signer.get_public_key().as_hex()

    def deposit(self, value):
        return self._wrap_and_send("deposit", value)

    def withdraw(self, value):
        try:
            return self._wrap_and_send("withdraw", value)
        except Exception:
            raise Exception('Error during withdrawal')

    def transfer(self, value, clientToKey):
        try:
            with open(clientToKey) as fd:
                publicKeyStr = fd.read().strip()
            return self._wrap_and_send("transfer", value, publicKeyStr)
        except OSError as err:
            raise Exception(f'Failed to read public key {clientToKey}: {str(err)}')

    def balance(self):
        result = self._send_to_restapi(f"state/{self._address}")
        try:
            return base64.b64decode(yaml.safe_load(result)["data"])
        except Exception:
            return None

    def _send_to_restapi(self, suffix, data=None, contentType=None):
        url = f"{self._baseUrl}/{suffix}" if self._baseUrl.startswith("http://") else f"http://{self._baseUrl}/{suffix}"
        headers = {'Content-Type': contentType} if contentType else {}

        try:
            if data:
                result = requests.post(url, headers=headers, data=data)
            else:
                result = requests.get(url, headers=headers)

            if not result.ok:
                raise Exception(f"Error {result.status_code}: {result.reason}")
        except requests.ConnectionError as err:
            raise Exception(f'Failed to connect to {url}: {str(err)}')
        return result.text

    def _wrap_and_send(self, action, *values):

        # create payload 
        rawPayload = action + "," + ",".join(str(val) for val in values)
        print(rawPayload)
        payload = rawPayload.encode()
        print(payload)

        #addressing
        inputAddressList = [self._address]
        outputAddressList = [self._address]

        # if operation is transfer add destination
        if action == "transfer":
            toAddress = _hash(FAMILY_NAME.encode('utf-8'))[0:6] + _hash(values[1].encode('utf-8'))[0:64]
            inputAddressList.append(toAddress)
            outputAddressList.append(toAddress)

        # default
        header = TransactionHeader(
            signer_public_key=self._publicKey,
            family_name=FAMILY_NAME,
            family_version="1.0",
            inputs=inputAddressList,
            outputs=outputAddressList,
            dependencies=[],
            payload_sha512=_hash(payload),
            batcher_public_key=self._publicKey,
            nonce=random.random().hex().encode()
        ).SerializeToString()

        transaction = Transaction(
            header=header,
            payload=payload,
            header_signature=self._signer.sign(header)
        )

        batchHeader = BatchHeader(
            signer_public_key=self._publicKey,
            transaction_ids=[transaction.header_signature]
        ).SerializeToString()

        batch = Batch(
            header=batchHeader,
            transactions=[transaction],
            header_signature=self._signer.sign(batchHeader)
        )

        batchList = BatchList(batches=[batch])
        return self._send_to_restapi("batches", batchList.SerializeToString(), 'application/octet-stream')
