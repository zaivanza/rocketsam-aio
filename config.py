import asyncio
from modules.utils.files import read_txt, load_json
from modules.utils.helpers import get_chain_prices, get_wallet_proxies, get_bungee_data

max_time_check_tx_status = 100  # seconds. If a transaction does not return a status within this time, it is considered executed

STR_DONE = '✅ '
STR_CANCEL = '❌ '

ERC20_ABI = load_json("modules/utils/contracts/erc20.json")
MULTICALL_ABI = load_json("modules/utils/contracts/multicall_abi.json")
WALLETS = read_txt("datas/wallets.txt")
RECIPIENTS = read_txt("datas/recipients.txt")
STARKNET_KEYS = read_txt("datas/starknet_keys.txt")
STARKNET_ADDRESSES = read_txt("datas/starknet_addresses.txt")
PROXIES = read_txt("datas/proxies.txt")
ORBITER_MAKER = load_json("modules/utils/contracts/orbiter_maker.json") # https://github.com/Orbiter-Finance/OrbiterFE-V2/tree/main/src/config (maker-1 / maker-2)
ABI_ZERIUS_REFUEL = load_json("modules/utils/contracts/zerius_refuel.json")

RECIPIENTS_WALLETS = dict(zip(WALLETS, RECIPIENTS))
STARKNET_WALLETS = dict(zip(WALLETS, STARKNET_ADDRESSES))

WALLET_PROXIES = get_wallet_proxies(WALLETS, PROXIES)
PRICES_NATIVE = asyncio.run(get_chain_prices())
BUNGEE_LIMITS = asyncio.run(get_bungee_data())