from config import STR_CANCEL, STR_DONE
from .utils.contracts.abi import ABI_ROCKETSAM, STARKNET_ETH_ABI
from .utils.contracts.contract import ROCKETSAM_CONTRACTS, STARKNET_ETH_CONTRACT
from .utils.helpers import list_send, intToDecimal, async_sleeping, decimalToInt, round_to, deserialize_uint256, serialize_uint256
from .utils.manager_async import Web3ManagerAsync
from setting import Value_RocketSam, RETRY, IS_SLEEP, DELAY_SLEEP
from datas.data import DATA, STARKNET_RPC, STARKNET_SCANNER, STARKNET_DEPOSIT_GAS, STARKNET_WITHDRAW_GAS

from loguru import logger
from web3 import Web3
import random
import asyncio
from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call, TransactionExecutionStatus, TransactionFinalityStatus
from json import loads as json_load

class RocketSam:

    STARKNET = 'starknet'

    GAS_MULTIPLIER = 3 # Multiplier for gas to ensure sufficient for withdrawal
    
    def __init__(self, chain: str, key: str, number: str, stark_key: str = '', stark_address: str = ''):
        self.number = number
        self.chain = chain
        if (self.chain == self.STARKNET):
            self.stark_key = stark_key
            self.stark_address = stark_address
        else:
            self.key = key
        self.amount_interactions = random.randint(*Value_RocketSam.amount_interactions)
        self.deposit_all_balance = Value_RocketSam.deposit_all_balance
        self.deposit_value = Value_RocketSam.deposit_value
        self.module = Value_RocketSam.module
        self.keep_values = Value_RocketSam.keep_values

    async def setup_starknet(self):
        client = FullNodeClient(node_url=STARKNET_RPC)
        key_pair = KeyPair.from_private_key(key=self.stark_key)
        self.account = Account(
            client=client,
            address=self.stark_address,
            key_pair=key_pair,
            chain=StarknetChainId.MAINNET,
        )
        self.module_str = f'{self.number} {self.stark_address} | rocketsam [{self.STARKNET}]'
        self.eth_contract =  Contract(
            address=STARKNET_ETH_CONTRACT,
            abi=json_load(STARKNET_ETH_ABI),
            provider=self.account,
        )
        keep_value = round(random.uniform(self.keep_values[0], self.keep_values[1]), 8)
        if self.deposit_all_balance: 
            balance = await self.eth_contract.functions['balanceOf'].call(int(self.stark_address, 0))
            self.amount = balance - keep_value
        else: 
            self.amount = round(random.uniform(self.deposit_value[0], self.deposit_value[1]), 8)
        self.value = intToDecimal(self.amount, 18)
        self.keeper = intToDecimal(0.0001, 18) # ~0.2$ We leave that much when we deposit the entire balance
    
    async def get_stark_contract(self, stark_contract_address: str) -> Contract:
        return await Contract.from_address(
            address=stark_contract_address,
            provider=self.account,
        )
    
    async def get_stark_pool_contract_with_least_txs(self) -> Contract:
        logger.info('Searching for the pool with the least number of interactions')

        random.shuffle(ROCKETSAM_CONTRACTS[self.STARKNET])
        contracts = { address: await self.get_stark_contract(address) for address in ROCKETSAM_CONTRACTS[self.STARKNET] }
        pools = { 
            address : 
                await contract.functions['getAddressStatistics'].call(
                    self.account.address
                ) for (address, contract) in contracts.items()
        }

        min_tx_pool = min(contracts, key = lambda pool_address: pools[pool_address][0])
        return contracts[min_tx_pool]
    
    async def get_stark_pools_with_balance(self) -> list[Contract]:
        contract_addresses = ROCKETSAM_CONTRACTS[self.STARKNET]
        contracts = { address: await self.get_stark_contract(address) for address in contract_addresses }
        pools = []
        for address in contract_addresses:
            balance = deserialize_uint256(await contracts[address].functions['getBalance'].call(int(self.stark_address, 0)))
            if (balance > 0):
                pools.append(address)
                
        return pools
    
    async def stark_deposit(self, contract: Contract, module: int) -> (str | None, TransactionExecutionStatus | None):
        try:
            stark_dep_amount = serialize_uint256(self.value)
            fee = deserialize_uint256(await contract.functions['estimateProtocolFee'].call(stark_dep_amount))

            if self.deposit_all_balance:
                if module   == 1: multiplier = 1
                elif module == 2: multiplier = self.GAS_MULTIPLIER 
                self.dep_amount = int(self.value - fee - (STARKNET_DEPOSIT_GAS * multiplier) * 0.9999) - self.keeper
            else:
                self.dep_amount = self.value

            if self.dep_amount < 0:
                logger.error(f'{self.module_str} | amount < 0')
                return (None, None)

            allowance = deserialize_uint256(await self.eth_contract.functions['allowance'].call(
                int(self.stark_address, 0), 
                contract.data.address
            ))
            
            calls = []
            if (fee + self.dep_amount > allowance):
                approve_value = serialize_uint256(fee + self.dep_amount)
                approve_call = Call(
                    to_addr=int(STARKNET_ETH_CONTRACT, 0),
                    selector=get_selector_from_name("approve"),
                    calldata=[contract.data.address, approve_value[0], approve_value[1]],
                )
                calls.append(approve_call)

            dep_amount = serialize_uint256(self.dep_amount)
            calls.append(
                Call(
                    to_addr=contract.address,
                    selector=get_selector_from_name("deposit"),
                    calldata=[dep_amount[0], dep_amount[1]],
                )
            )

            resp = await self.account.execute(calls=calls, max_fee=STARKNET_DEPOSIT_GAS)
            tx = await self.account.client.wait_for_tx(resp.transaction_hash)
            tx_hash = hex(tx.transaction_hash)
            tx_status = tx.execution_status
            return (tx_hash, tx_status)
        except Exception as error:
            logger.error(f'{self.module_str} | error while depositing: {error}')
            return (None, None)
    
    async def stark_withdraw(self, contract: Contract) -> (str | None, TransactionExecutionStatus | None):
        try:
            invocation = await contract.functions['withdraw'].invoke(max_fee=STARKNET_WITHDRAW_GAS)
            tx = await invocation.wait_for_acceptance()
            tx_hash = hex(tx.hash)
            tx_status = tx.status
            if (tx_status == TransactionFinalityStatus.ACCEPTED_ON_L2): 
                tx_status = TransactionExecutionStatus.SUCCEEDED
            print(tx_status)
            return (tx_hash, tx_status)
        except Exception as error:
            logger.error(f'{self.module_str} | error while withdrawing: {error}')
            return (None, None)
        
    async def stark_invoke_retry(self, contract, txn_type) -> bool:
        retry = 0
        tx_hash = None
        tx_status = None
        while ((tx_hash == None or tx_status != TransactionExecutionStatus.SUCCEEDED) and retry <= RETRY):
            tx_hash = None
            tx_status = None

            match txn_type:
                case 'deposit':
                    (tx_hash, tx_status) = await self.stark_deposit(contract, self.module)
                case 'withdraw':
                    (tx_hash, tx_status) = await self.stark_withdraw(contract)

            if (tx_hash != None): tx_link = f'{STARKNET_SCANNER}/tx/{tx_hash}'
            else: tx_link = None

            retry += 1

            if (tx_status != TransactionExecutionStatus.SUCCEEDED):
                if (tx_link == None):
                    logger.error(f'{self.module_str} | {txn_type} | tx failed')
                else:
                    logger.error(f'{self.module_str} | {txn_type} | tx failed | {tx_link}')
                await asyncio.sleep(5)
            elif tx_status == TransactionExecutionStatus.SUCCEEDED:
                if (txn_type == "deposit"):
                    logger.success(f'{self.module_str} | {txn_type} {round_to(decimalToInt(self.dep_amount, 18))} {DATA[self.chain]["token"]} | {tx_link}')
                else:
                    logger.success(f'{self.module_str} | {txn_type} | {tx_link}')
        return (tx_status == TransactionExecutionStatus.SUCCEEDED)
    
    async def stark_invoke_tx(self) -> list[(bool, str)]:
        match self.module:
            case 1:
                contract = await self.get_stark_contract_with_least_txs()
                success = await self.stark_invoke_retry(contract, 'deposit')
                return [(success, 'deposit')]
            case 2:
                contract = await self.get_stark_contract_with_least_txs()
                deposit_success = await self.stark_invoke_retry(contract, 'deposit')
                if (deposit_success):
                    await async_sleeping(*DELAY_SLEEP)
                    withdraw_success = await self.stark_invoke_retry(contract, 'withdraw')
                else: withdraw_success = False
                return [(deposit_success, 'deposit'), (withdraw_success, 'withdraw')]
            case 3:
                contract_addresses = await self.get_stark_pools_with_balance()
                contracts = [await self.get_stark_contract(address) for address in contract_addresses]
                withdraw_txs_success = [(await self.stark_invoke_retry(contract, 'withdraw'), 'withdraw') for contract in contracts]
                return withdraw_txs_success

    async def setup(self):
        self.manager = Web3ManagerAsync(self.key, self.chain)
        self.amount = await self.manager.get_amount_in(
            self.keep_values[0], self.keep_values[1], self.deposit_all_balance, '', self.deposit_value[0], self.deposit_value[1]
        )
        self.token_data = await self.manager.get_token_info('')
        self.value = intToDecimal(self.amount, 18)
        self.module_str = f'{self.number} {self.manager.address} | rocketsam [{self.chain}]'
        self.keeper = intToDecimal(0.0001, 18) # ~0.2$ We leave that much when we deposit the entire balance

    async def get_contract(self, contract_address: str):
        return self.manager.web3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=ABI_ROCKETSAM)

    async def get_contract_with_least_number_txs(self):
        logger.info('Searching for the pool with the least number of interactions')
        random.shuffle(ROCKETSAM_CONTRACTS[self.chain])
        pools = {}
        for contract_address in ROCKETSAM_CONTRACTS[self.chain]:
            depositsCount, depositsVolume = await self.get_address_pool_statistic(contract_address)
            pools[contract_address] = depositsCount
        return min(pools, key=pools.get)
    
    async def get_deposit_fee(self, contract_address: str, value: int):
        contract = await self.get_contract(contract_address)
        fee = await contract.functions.estimateProtocolFee(value).call()
        return fee

    async def get_address_pool_statistic(self, contract_address: str):
        contract = await self.get_contract(contract_address)
        statistic = await contract.functions.addressStatistic(self.manager.address).call()
        depositsCount = statistic[0]
        depositsVolume = statistic[1]
        return depositsCount, depositsVolume
    
    async def get_wallet_contract_balance(self, contract_address: str):
        contract = await self.get_contract(contract_address)
        return await contract.functions.balances(self.manager.address).call()

    async def get_contract_pools_with_balance(self):
        pools = []
        for contract_address in ROCKETSAM_CONTRACTS[self.chain]:
            balance = await self.get_wallet_contract_balance(contract_address)
            if balance > 0:
                pools.append(contract_address)
        return pools

    async def get_deposit_txn(self, module: int):
        try:
            contract_address = await self.get_contract_with_least_number_txs()
            contract = await self.get_contract(contract_address)
            fee = await self.get_deposit_fee(contract_address, self.value)

            # pass value 1 for gas counting
            contract_txn = await contract.functions.deposit(1).build_transaction(
                {
                    "from": self.manager.address,
                    "value": 1 + fee,
                    "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                    'gasPrice': await self.manager.web3.eth.gas_price,
                }
            )

            contract_txn["gas"] = int(contract_txn["gas"] * 1.2)

            if self.deposit_all_balance:
                if module   == 1: multiplier = 1
                elif module == 2: multiplier = self.GAS_MULTIPLIER 
                amount = int(self.value - fee - (contract_txn["gas"] * contract_txn["gasPrice"] * multiplier) * 0.9999) - self.keeper
                value = int(amount + fee)
            else:
                amount = self.value
                value = int(amount + fee)

            if amount < 0:
                logger.error(f'{self.module_str} | amount < 0')
                return False, contract_address
            
            contract_txn = await contract.functions.deposit(amount).build_transaction(
                {
                    "from": self.manager.address,
                    "value": value,
                    "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address),
                    'gasPrice': await self.manager.web3.eth.gas_price,
                    "gas": contract_txn["gas"]
                }
            )

            if self.manager.get_total_fee(contract_txn) == False: 
                return False, contract_address

            return contract_txn, contract_address

        except Exception as error:
            logger.error(f'{self.module_str} | {error}')
            # list_send.append(f'{STR_CANCEL}{self.module_str} | deposit | {error}')
            return False, contract_address
        
    async def get_withdraw_txn(self, contract_address: str, plus_nonce=0):
        try:
            balance = await self.get_wallet_contract_balance(contract_address)
            if balance > 0:
                contract = await self.get_contract(contract_address)
                contract_txn = await contract.functions.withdraw().build_transaction(
                    {
                        "from": self.manager.address,
                        "value": 0,
                        "nonce": await self.manager.web3.eth.get_transaction_count(self.manager.address) + plus_nonce,
                        'gasPrice': await self.manager.web3.eth.gas_price,
                    }
                )

                contract_txn["gas"] = int(contract_txn["gas"] * 1.1)

                if self.manager.get_total_fee(contract_txn) == False: return False
                return contract_txn
            else:
                logger.error('Cannot withdraw, your pool balance is 0')
                # list_send.append(f'{STR_CANCEL}{self.module_str} | withdraw | your pool balance is 0')
                return False
        except Exception as error:
            logger.error(error)
            # list_send.append(f'{STR_CANCEL}{self.module_str} | withdraw | {error}')
            return False
        
    async def perform_transactions(self):
        txns = []
        if self.module == 1:
            contract_txn, _ = await self.get_deposit_txn(self.module)
            if contract_txn:
                txns.append(("deposit", contract_txn))

        elif self.module == 2:
            deposit_contract_txn, contract_address = await self.get_deposit_txn(self.module)
            if deposit_contract_txn:
                txns.append(("deposit", deposit_contract_txn))
                txns.append(("prepare_withdraw", contract_address))

        elif self.module == 3:
            pools_with_balance = await self.get_contract_pools_with_balance()
            for i, contract_address in enumerate(pools_with_balance):
                contract_txn = await self.get_withdraw_txn(contract_address, plus_nonce=i)
                if contract_txn:
                    txns.append(("withdraw", contract_txn))
        
        return txns
    
    async def send_transaction_with_retry(self, txn_type: str, txn_data):
        attempts = 0
        while attempts <= RETRY:
            if not txn_data:
                logger.error(f'{self.module_str} | {txn_type} | error getting contract_txn')
                attempts += 1
                continue
        
            if txn_type == "deposit" or txn_type == "withdraw":
                status, tx_link = await self.manager.send_tx(txn_data)
            elif txn_type == "prepare_withdraw":
                txn_data = await self.get_withdraw_txn(txn_data)
                if txn_data:
                    status, tx_link = await self.manager.send_tx(txn_data)
                    txn_type = "withdraw"
                else:
                    status, tx_link = None, "error"

            if status == 1:
                if txn_type == "deposit":
                    logger.success(f'{self.module_str} | {txn_type} {round_to(decimalToInt(txn_data["value"], 18))} {DATA[self.chain]["token"]} | {tx_link}')
                else:
                    logger.success(f'{self.module_str} | {txn_type} | {tx_link}')
                return True
            elif status == 0:
                logger.error(f'{self.module_str} | {txn_type} | tx is failed | {tx_link}')
            else:
                logger.error(f'{self.module_str} | {txn_type} | {tx_link}')

            attempts += 1
            await asyncio.sleep(5) 

        return False
    
    async def main(self):
        for _ in range(self.amount_interactions):
            if (self.chain == self.STARKNET):
                await self.setup_starknet()
                txs_success = await self.stark_invoke_tx()
                for (success, txn_type) in txs_success:
                    if success:
                        list_send.append(f'{STR_DONE}{self.module_str} | {txn_type}')
                    else:
                        list_send.append(f'{STR_CANCEL}{self.module_str} | {txn_type}')

            else:
                await self.setup()
                txns = await self.perform_transactions()
                for txn_type, txn_data in txns:
                    success = await self.send_transaction_with_retry(txn_type, txn_data)
                    if txn_type == "prepare_withdraw":
                        txn_type = "withdraw"

                    if success:
                        list_send.append(f'{STR_DONE}{self.module_str} | {txn_type}')
                    else:
                        list_send.append(f'{STR_CANCEL}{self.module_str} | {txn_type}')

            if IS_SLEEP:
                await async_sleeping(*DELAY_SLEEP)
