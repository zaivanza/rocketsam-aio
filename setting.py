# --- Settings ---
WALLETS_IN_BATCH = 1    # How many wallets to run in one thread (simultaneously)

IS_SLEEP = True         # Enable/disable delay between wallets
DELAY_SLEEP = [5, 10]  # Delay range between wallets (seconds)
RANDOMIZER = True      # Enable/disable random wallet shuffling
RETRY = 0               # Number of retries on errors/failures
TG_BOT_SEND = True      # Enable/disable sending results to a Telegram bot

USE_PROXY = False       # Enable/disable proxy usage in web3 requests
CHECK_GWEI = False      # Enable/disable base Gwei checking
MAX_GWEI = 25           # Maximum Gwei (see https://etherscan.io/gastracker)

# Maximum transaction fee in USD, at which the script will sleep for 30 seconds and retry
MAX_GAS_CHARGE = {
    'arbitrum'      : 0.5,
    'linea'         : 1,
    'zksync'        : 1,
    'nova'          : 0.1,
    'polygon_zkevm' : 0.5,
    'base'          : 0.5,
    'scroll'        : 0.5,
    'zora'          : 0.5,
    'starknet'      : 1
}

class Value_RocketSam:
    """
    Module Options:
    1. Deposit.
    2. Deposit + Withdraw.
    3. Withdraw from all pools.

    Available chains: arbitrum | base | nova | linea | scroll | zora
    Attention! If you use tracks, change chain to the one you want to use
    """

    module = 2 # Option selection for the module's behavior (valid options: 1, 2, or 3)

    chain = ["starknet"] # List of blockchain networks to interact with
    
    amount_interactions = [2, 3] # Range of the number of times to interact with contracts, range should be >= 1 for both values
    deposit_all_balance = True # Flag to deposit the entire wallet balance (set to True to activate)
    keep_values = [0, 0] # Range of native tokens to retain in the wallet balance (effective only when deposit_all_balance = True). Specify the minimum and maximum amount to keep
    deposit_value = [0.0001, 0.0005] # Range for deposit value in native tokens (effective only when deposit_all_balance = False). Specify the minimum and maximum deposit amount
