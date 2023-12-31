from config import STR_CANCEL
from .utils.contracts.abi import ABI_ARBITRUM_BRIDGE
from .utils.helpers import round_to, list_send, intToDecimal
from .utils.manager_async import Web3ManagerAsync

from loguru import logger
from web3 import Web3

class ArbitrumBridge:
    
    def __init__(self, key, number, params):
        self.params = params
        self.from_chain = "ethereum"
        self.to_chain = "nova"
        self.amount_from = self.params['amount_from']
        self.amount_to = self.params['amount_to']
        self.bridge_all_balance = self.params['bridge_all_balance']
        self.min_amount_bridge = self.params['min_amount_bridge']
        self.keep_value_from = self.params['keep_value_from']
        self.keep_value_to = self.params['keep_value_to']

        self.key = key
        self.number = number

    async def setup(self):
        self.manager = Web3ManagerAsync(self.key, self.from_chain)
        self.amount = await self.manager.get_amount_in(self.keep_value_from, self.keep_value_to, self.bridge_all_balance, '', self.amount_from, self.amount_to)
        self.token_data = await self.manager.get_token_info('')
        self.value = intToDecimal(self.amount, 18)
        self.module_str = f'{self.number} {self.manager.address} | arbitrum_bridge : {self.from_chain} => {self.to_chain}'
        self.contract = self.manager.web3.eth.contract(address=Web3.to_checksum_address("0xc4448b71118c9071Bcb9734A0EAc55D18A153949"), abi=ABI_ARBITRUM_BRIDGE)

    async def get_txn(self):

        try:
            contract_txn = await self.contract.functions.depositEth().build_transaction(
                {
                    "from": self.manager.address,
                    "value": self.amount,
                    "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                    'gasPrice': 0,
                    'gas': 0,
                }
            )

            contract_txn = await self.manager.add_gas_price(contract_txn)
            contract_txn = await self.manager.add_gas_limit(contract_txn)

            if self.manager.get_total_fee(contract_txn) == False: return False

            if self.bridge_all_balance:
                gas_gas = int(contract_txn['gas'] * contract_txn['gasPrice'])
                contract_txn['value'] = contract_txn['value'] - gas_gas

            if self.amount >= self.min_amount_bridge:
                return contract_txn
            else:
                logger.error(f"{self.module_str} | {self.amount} (amount) < {self.min_amount_bridge} (min_amount_bridge)")
                list_send.append(f'{STR_CANCEL}{self.module_str} | {round_to(self.amount)} less {self.min_amount_bridge}')
                return False
            
        except Exception as error:
            logger.error(error)
            list_send.append(f'{STR_CANCEL}{self.module_str} | {error}')
            return False
