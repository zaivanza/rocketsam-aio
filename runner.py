from config import WALLETS, STR_DONE, STR_CANCEL
from setting import (
    RANDOMIZER, CHECK_GWEI, TG_BOT_SEND, IS_SLEEP, DELAY_SLEEP, RETRY, WALLETS_IN_BATCH
)
from modules.utils.helpers import list_send, wait_gas, send_msg, async_sleeping
from modules.utils.manager_async import Web3ManagerAsync
from modules import *
from tracks import *

from loguru import logger
import random
import inquirer
import asyncio

chains_tracks = {
    "zksync": zksync_tracks,
    "starknet": starknet_tracks,
    "base": base_tracks,
    "scroll": scroll_tracks,
    "zora": zora_tracks,
    "linea": linea_tracks,
    # "polygon_zkevm": polygon_zkevm_tracks,
    "arbitrum_nova": nova_tracks,
}

modules = {
    "exchange_withdraw": ExchangeWithdraw,
    "okx_withdraw": OkxWithdraw,
    "transfer": Transfer, 
    "orbiter_bridge": OrbiterBridge,
    "bungee_refuel": BungeeRefuel,
    "zerius_refuel": ZeriusRefuel, 
    "starkgate": Starkgate, 
    "zksync_bridge": ZkSyncBridge, 
    "zora_bridge": ZoraBridge, 
    "base_bridge": BaseBridge, 
    "arbitrum_bridge": ArbitrumBridge, 
    "rocketsam": RocketSam
}

def get_module(module: str):
    try:
        return modules[module]
    except KeyError:
        raise ValueError(f"Unsupported module: {module}")
    
async def handle_transaction(module_name: str, params: dict, key: str, number: str):
    """Processes a single transaction within a track"""
    func = get_module(module_name)
    func_instance = func(key, number, params)
    await func_instance.setup()
    logger.debug(f'{func_instance.module_str}')
    return await func_instance.get_txn(), func_instance, module_name

async def execute_transaction(transaction: dict, func_instance):
    """Executes the transaction with retries in case of failure"""
    attempts = 0
    while attempts < RETRY:
        status, tx_link = await func_instance.manager.send_tx(transaction)

        if not status:
            list_send.append(f'{STR_CANCEL}{func_instance.module_str}')
            break
        elif status == 1:
            logger.success(f'{func_instance.module_str} | {tx_link}')
            list_send.append(f'{STR_DONE}{func_instance.module_str}')
            return True
        else:
            logger.error(f'{func_instance.module_str} | tx failed | {tx_link}')
            await asyncio.sleep(10) # Pause before the next attempt
        attempts += 1
    return False

async def worker_tracks(key: str, number: str, track: dict):
    """Handler for tasks defined in tracks."""
    for params in track:
        if params['module_name'] == 'wait_balance':
            # Handling balance waiting
            manager = Web3ManagerAsync(key, params['params']['chain'])
            await manager.wait_balance(number, params['params']['min_balance'], params['params']['token'])
            continue

        if params['module_name'] == 'sleeping':
            # Handling sleep
            time_sleep = random.randint(int(params['params']['from']), int(params['params']['to']))
            logger.info(f'sleep for {time_sleep} sec.')
            await asyncio.sleep(time_sleep)
            continue

        if params['module_name'] == 'rocketsam':
            # Handling the RocketSam module
            rocket_sam_instance = RocketSam(key, number)
            await rocket_sam_instance.main()
            continue

        if params['module_name'] in ["exchange_withdraw", "okx_withdraw"]:
            # Handling exchanges modules
            func = get_module(params['module_name'])
            exchange = func(key, params['params'])
            await exchange.start()
            continue
               
        # Handling other modules
        transaction, func_instance, module_name = await handle_transaction(params['module_name'], params['params'], key, number)
        if not transaction:
            logger.error(f'{number} | error getting transaction')
            list_send.append(f'{STR_CANCEL}{module_name}')
            break # Break the loop if the transaction fails

        success = await execute_transaction(transaction, func_instance)
        if not success:
            logger.error(f'{number} | module not successful, cycle broken')
            break # Break the loop if the transaction fails

async def main_workflow(wallet_batches: list, track=None):
    index = 0
    for batch in wallet_batches:
        if CHECK_GWEI:
            await wait_gas()

        tasks = []
        for wallet_key in batch:
            index += 1
            if track:
                tasks.append(asyncio.create_task(worker_tracks(wallet_key, f'[{index}/{len(WALLETS)}]', track)))
            else:
                rocket_sam_instance = RocketSam(wallet_key, f'[{index}/{len(WALLETS)}]')
                tasks.append(asyncio.create_task(rocket_sam_instance.main()))

        await asyncio.gather(*tasks)

        if TG_BOT_SEND and list_send:
            send_msg()
            list_send.clear()

        if IS_SLEEP and track:
            await async_sleeping(*DELAY_SLEEP)

async def main():
    if RANDOMIZER:
        random.shuffle(WALLETS)

    batches = [WALLETS[i:i + WALLETS_IN_BATCH] for i in range(0, len(WALLETS), WALLETS_IN_BATCH)]

    use_tracks = inquirer.prompt([
        inquirer.List('use_tracks', message="What are we doing?", choices=["Use tracks", "Use only rocketsam module"], carousel=True)
    ])['use_tracks']
    
    if use_tracks == "Use tracks":
        chains = list(chains_tracks.keys())
        chain = inquirer.prompt([inquirer.List('correct', message="Choose a chain: ", choices=chains, carousel=True)])['correct']
        chain_tracks = ['{}. {}'.format(i, ' => '.join([f'{data["module_name"]} {data.get("description", "")}'.strip() 
                        for data in track if data["module_name"] not in ["wait_balance", "sleeping"]]))
                        for i, track in enumerate(chains_tracks[chain], start=1)]
        track_id = inquirer.prompt([inquirer.List('correct', message="Choose a track: ", choices=chain_tracks, carousel=True)])['correct'].split('.')[0]
        selected_track = chains_tracks[chain][int(track_id) - 1]

        await main_workflow(batches, selected_track)
    else:
        await main_workflow(batches)