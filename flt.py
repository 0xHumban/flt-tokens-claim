import os
from datetime import datetime, timedelta, timezone
import pytz
from tzlocal import get_localzone

from web3 import Web3

FLT_ABI = '[{"inputs":[{"internalType":"contract FluenceToken","name":"_token","type":"address"},{"internalType":"contract Executor","name":"_executor","type":"address"},{"internalType":"bytes32","name":"_merkleRoot","type":"bytes32"},{"internalType":"uint256","name":"_halvePeriod","type":"uint256"},{"internalType":"uint256","name":"_lockupPeriod","type":"uint256"},{"internalType":"uint256","name":"_initialReward","type":"uint256"},{"internalType":"uint256","name":"_claimingPeriod","type":"uint256"},{"internalType":"address","name":"_canceler","type":"address"},{"internalType":"uint256","name":"_maxClaimedSupply","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"address","name":"target","type":"address"}],"name":"AddressEmptyCode","type":"error"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"AddressInsufficientBalance","type":"error"},{"inputs":[],"name":"ECDSAInvalidSignature","type":"error"},{"inputs":[{"internalType":"uint256","name":"length","type":"uint256"}],"name":"ECDSAInvalidSignatureLength","type":"error"},{"inputs":[{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"ECDSAInvalidSignatureS","type":"error"},{"inputs":[],"name":"FailedInnerCall","type":"error"},{"inputs":[{"internalType":"address","name":"token","type":"address"}],"name":"SafeERC20FailedOperation","type":"error"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"userId","type":"uint256"},{"indexed":false,"internalType":"address","name":"account","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"bytes32","name":"leaf","type":"bytes32"}],"name":"Claimed","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"TransferUnclaimed","type":"event"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"canceler","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint32","name":"userId","type":"uint32"},{"internalType":"bytes32[]","name":"merkleProof","type":"bytes32[]"},{"internalType":"address","name":"temporaryAddress","type":"address"},{"internalType":"bytes","name":"signature","type":"bytes"}],"name":"claimTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"claimedSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"claimingEndTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"currentReward","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"deployTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"executor","outputs":[{"internalType":"contract Executor","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"halvePeriod","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"initialReward","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"index","type":"uint256"}],"name":"isClaimed","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"isClaimingActive","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"lockedBalances","outputs":[{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"unlockTime","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"lockupPeriod","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"maxClaimedSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"merkleRoot","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"token","outputs":[{"internalType":"contract FluenceToken","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"}]'


class FLT:
    def __init__(self, http_provider_url, contract_address, private_key):
        self.w3 = Web3(Web3.HTTPProvider(http_provider_url))
        self.contract_abi = FLT_ABI
        self.contract_address = self.w3.to_checksum_address(contract_address)
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.contract_abi)
        self.private_key = private_key
        self.public_address = self.get_public_address()

    """
        returns the public key of the user from his private key
    """

    def get_public_address(self):
        # create signer account
        pa = self.w3.eth.account.from_key(self.private_key)
        return pa.address

    """
        returns the $FLT-DROP balance of the user
    """

    def get_flt_drop_balance(self):
        return self.contract.functions.balanceOf(self.public_address).call()

    """
        returns decimal number of $FLT-DROP
    """

    def get_decimals(self):
        return self.contract.functions.decimals().call()

    """
        returns a tuple with the locked balances information
    """

    def get_locked_balances(self):
        return self.contract.functions.lockedBalances(self.public_address).call()

    """
        send a transaction from a account,
        :returns transaction hash
    """

    def send_transaction(self, tx, private_key):
        signed_transaction = self.w3.eth.account.sign_transaction(tx, private_key)
        return self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

    """
        build a transaction
        :returns unsigned transaction
    """

    def build_transaction(self, from_address, value, to, gas, gas_price, data):
        nonce = self.w3.eth.get_transaction_count(self.public_address)
        chain_id = self.w3.eth.chain_id
        return {
            'from': self.w3.to_checksum_address(from_address),
            'value': value,
            'to': self.w3.to_checksum_address(to),
            'nonce': nonce,
            'gas': gas,
            'maxFeePerGas': gas_price,
            'maxPriorityFeePerGas': gas_price,
            'chainId': chain_id,
            'data': data
        }

    """
        returns the gas estimate for a transaction
    """

    def get_gas_estimate(self, from_address, to, value, data):
        return self.w3.eth.estimate_gas({
            'from': from_address,
            'to': to,
            'value': value,
            'data': data
        })

    """
        Transfer token to the receiver address
        :returns transaction hash
    """

    def transfer(self, receiver_address, token_balance):
        encode_abi = self.contract.encodeABI(fn_name="transfer", args=[
            receiver_address,
            token_balance
        ])
        gas_limit = self.get_gas_estimate(self.public_address, self.contract_address, 0, encode_abi)
        gas_price = self.w3.eth.gas_price
        tx = self.build_transaction(self.public_address, 0, self.contract_address, gas_limit, gas_price, encode_abi)
        return self.send_transaction(tx, self.private_key)

    """
        send transaction to transfer tokens to yourself
        :returns transaction hash
    """

    def transfer_to_yourself(self, token_balance):
        return self.transfer(self.public_address, token_balance)

    # PRINT PART

    """
        Transfer tokens to yourself
    """

    def perform_transfer_to_yourself(self):
        token_balance = self.get_flt_drop_balance()
        tx_hash = self.transfer_to_yourself(token_balance)
        self.get_transaction_info(tx_hash)

    """
        wait for the transaction result
    """

    def get_transaction_info(self, tx_hash):
        res = self.w3.eth.wait_for_transaction_receipt(tx_hash, poll_latency=0.5)
        if res.status == 0:
            print("\nTransaction reverted: ", tx_hash.hex(), "\n")
        else:
            print("\nTransaction passed: ", tx_hash.hex(), "\n")

    """
        show the unlock time to the user
    """

    def show_unlock_time(self):
        locked_balances = self.get_locked_balances()
        unlock_timestamp = locked_balances[1]
        # print("Timestamp: ", unlock_timestamp)
        utc_datetime = datetime.utcfromtimestamp(unlock_timestamp)

        # get local timezone
        local_timezone = get_localzone()

        utc_date = datetime.utcfromtimestamp(unlock_timestamp)
        local_datetime = utc_datetime.astimezone(local_timezone)

        now = datetime.now(local_timezone)

        print("\nUnlock date: \nUTC: ", utc_date.strftime("%Y-%m-%d %H:%M:%S"),
              "\nLocal: ", local_datetime.strftime("%Y-%m-%d %H:%M:%S"))

        print("\nUnlock in: \n\t", local_datetime - now)

    """
        show the $FLT-DROP balance of the user
    """

    def show_flt_drop_balance(self):
        user_balance = int(self.get_flt_drop_balance() / (10 ** self.get_decimals()))
        print("Balance of " + self.public_address + " : " + str(user_balance) + " $FLT-DROP")

    """
        check if the connexion to the provider is ok
    """

    def check_connexion(self):
        if self.w3.is_connected():
            print("Connected to the provider")
        else:
            print("Failed to connect to the provider")
