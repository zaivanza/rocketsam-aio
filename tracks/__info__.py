names_of_modules = '''

wait_balance
sleeping
exchange_withdraw
okx_withdraw
transfer
orbiter_bridge
bungee_refuel
zerius_refuel
starkgate_bridge
zksync_bridge
base_bridge
arbitrum_bridge
zora_bridge

'''

# Created to demonstrate how to configure each module
all_modules = [
    {
        'module_name': 'wait_balance', # Module Name
        'description': '(Arbitrum)', # Additional Module Description
        'params': {
            'chain': 'Arbitrum', # Network where we are awaiting coins
            'min_balance': 0.01, # Script proceeds to next module when balance exceeds this number
            'token': '', # Token address. Leave empty for native token
        },
    },
    {
        'module_name': 'sleeping', # Module Name
        'description': '(10-50s)', # Additional Module Description
        'params': {
            'from': 10, # Sleep duration starting from
            'to': 50, # Sleep duration up to
        },
    },
    {
        'module_name': 'exchange_withdraw', # Module Name
        'description': '(Binance ETH)', # Additional Module Description
        'params': {
            'cex': 'Binance', # Exchange Name. Options: Binance | Bybit | Kucoin | MEXC | Huobi | Bitget
            'chain': 'ETH', # Network
            'symbol': 'ETH', # Coin Symbol
            'amount_from': 10, # Minimum withdrawal amount
            'amount_to': 15.5, # Maximum withdrawal amount
            'is_private_key': True, # Set to True if EVM private keys are inserted in wallets.txt. Set to False for addresses (EVM / non-EVM).
        },
    },
    {
        'module_name': 'okx_withdraw', # Module Name
        'description': '(Arbitrum ETH)', # Additional Module Description
        'params': {
            'chain': 'Arbitrum One (Bridged)', # Network
            'symbol': 'ETH', # Coin Symbol
            'amount_from': 0.1, # Minimum withdrawal amount
            'amount_to': 0.2, # Maximum withdrawal amount
            'account': 'account_1', # Account for withdrawal. Refer to account names in data/data.py => OKX_KEYS
            'fee': 0.00001, # Withdrawal fee
            'sub_acc': True, # True / False. Set to True to check sub-accounts and transfer from them to the main account first
            'is_private_key': True, # Set to True if EVM private keys are inserted in wallets.txt. Set to False for addresses (EVM / non-EVM).
        },
    },
    {
        'module_name': 'transfer', # Module Name
        'description': '(Arbitrum ETH)', # Additional Module Description
        'params': {
            'chain': 'arbitrum', # Network to withdraw to
            'token_address': '', # Leave empty if it's the native token of the network
            'amount_from': 0.1, # Transfer from a certain amount of coins
            'amount_to': 0.2, # Transfer up to a certain amount of coins
            'transfer_all_balance': False, # True / False. If True, then transfer the entire balance
            'min_amount_transfer': 0.01, # If the balance is less than this amount, no transfer will be made
            'keep_value_from': 0, # How many coins to keep on the wallet (only works when: transfer_all_balance = True)
            'keep_value_to': 0, # Up to how many coins to keep on the wallet (only works when: transfer_all_balance = True)
        },
    },
    {
        'module_name': 'orbiter_bridge', # Module Name
        'description': '(arbitrum => optimism)', # Additional Module Description
        'params': {
            'from_chain': ['arbitrum'], # From which network
            'to_chain': ['optimism', 'zksync'], # To which network
            'amount_from': 0.1, # Transfer from a certain amount of coins
            'amount_to': 0.2, # Transfer up to a certain amount of coins
            'bridge_all_balance': True, # True / False. If True, then transfer the entire balance
            'min_amount_bridge': 0.01, # If the balance is less than this amount, no transfer will be made
            'keep_value_from': 0, # How many coins to keep on the wallet (only works when: bridge_all_balance = True)
            'keep_value_to': 0, # Up to how many coins to keep on the wallet (only works when: bridge_all_balance = True)
        },
    },
    {
        'module_name': 'bungee_refuel', # Module Name
        'description': '(arbitrum => zksync)', # Additional Module Description
        'params': {
            'from_chain': ['arbitrum'], # From which network
            'to_chain': ['zksync'], # To which network
            'amount_from': 0.003, # Refuel from a certain amount of coins
            'amount_to': 0.0036, # Refuel up to a certain amount of coins
            'bridge_all_balance': False, # True / False. If True, then refuel the entire balance
            'min_amount_bridge': 0.001, # If the balance is less than this amount, no refuel will be made
            'keep_value_from': 0, # How many coins to keep on the wallet (only works when: min_amount_bridge = True)
            'keep_value_to': 0, # Up to how many coins to keep on the wallet (only works when: min_amount_bridge = True)
        },
    },
    {
        'module_name': 'zerius_refuel', # Module Name
        'description': '(polygon => X chain)', # Additional Module Description
        'params': {
            'from_chain': ['polygon'], # From which network
            'to_chain': ['kava', 'nova', 'tenet', 'moonriver', 'moonbeam'], # To which network
            'amount_from': 0.0002, # Refuel from a certain amount of coins
            'amount_to': 0.003, # Refuel up to a certain amount of coins
            'swap_all_balance': False, # True / False. If True, then refuel the entire balance
            'min_amount_swap': 0, # If the balance is less than this amount, no refuel will be made
            'keep_value_from': 0, # How many coins to keep on the wallet (only works when: min_amount_swap = True)
            'keep_value_to': 0, # Up to how many coins to keep on the wallet (only works when: min_amount_swap = True)
        },
    },
    {
        'module_name': 'starkgate_bridge', # Module Name
        'description': '(eth => starknet)', # Additional Module Description
        'params': {
            'amount_from': 0, # Transfer from a certain amount of coins
            'amount_to': 0, # Transfer up to a certain amount of coins
            'bridge_all_balance': True, # True / False. If True, then transfer the entire balance
            'min_amount_bridge': 0.01, # If the balance is less than this amount, no transfer will be made
            'keep_value_from': 0, # How many coins to keep on the wallet (only works when: bridge_all_balance = True)
            'keep_value_to': 0, # Up to how many coins to keep on the wallet (only works when: bridge_all_balance = True)
        },
    },
    {
        'module_name': 'base_bridge', # Module Name
        'description': '(eth => base)', # Additional Module Description
        'params': {
            'amount_from': 0, # Transfer from a certain amount of coins
            'amount_to': 0, # Transfer up to a certain amount of coins
            'bridge_all_balance': True, # True / False. If True, then transfer the entire balance
            'min_amount_bridge': 0.01, # If the balance is less than this amount, no transfer will be made
            'keep_value_from': 0, # How many coins to keep on the wallet (only works when: bridge_all_balance = True)
            'keep_value_to': 0, # Up to how many coins to keep on the wallet (only works when: bridge_all_balance = True)
        },
    },
    {
        'module_name': 'zksync_bridge', # Module Name
        'description': '(eth => zksync)', # Additional Module Description
        'params': {
            'amount_from': 0, # Transfer from a certain amount of coins
            'amount_to': 0, # Transfer up to a certain amount of coins
            'bridge_all_balance': True, # True / False. If True, then transfer the entire balance
            'min_amount_bridge': 0.01, # If the balance is less than this amount, no transfer will be made
            'keep_value_from': 0, # How many coins to keep on the wallet (only works when: bridge_all_balance = True)
            'keep_value_to': 0, # Up to how many coins to keep on the wallet (only works when: bridge_all_balance = True)
        },
    },
    {
        'module_name': 'arbitrum_bridge', # Module Name
        'description': '(eth => nova)', # Additional Module Description
        'params': {
            'amount_from': 0, # Transfer from a certain amount of coins
            'amount_to': 0, # Transfer up to a certain amount of coins
            'bridge_all_balance': True, # True / False. If True, then transfer the entire balance
            'min_amount_bridge': 0.01, # If the balance is less than this amount, no transfer will be made
            'keep_value_from': 0, # How many coins to keep on the wallet (only works when: bridge_all_balance = True)
            'keep_value_to': 0, # Up to how many coins to keep on the wallet (only works when: bridge_all_balance = True)
        },
    },
    {
        'module_name': 'zora_bridge', # Module Name
        'description': '(eth => zora)', # Additional Module Description
        'params': {
            'amount_from': 0, # Transfer from a certain amount of coins
            'amount_to': 0, # Transfer up to a certain amount of coins
            'bridge_all_balance': True, # True / False. If True, then transfer the entire balance
            'min_amount_bridge': 0.01, # If the balance is less than this amount, no transfer will be made
            'keep_value_from': 0, # How many coins to keep on the wallet (only works when: bridge_all_balance = True)
            'keep_value_to': 0, # Up to how many coins to keep on the wallet (only works when: bridge_all_balance = True)
        },
    },
]
