###################### POLYGON_ZKEVM ######################

# POLYGON_ZKEVM : exc_withdraw (polygon_zkevm) => rocketsam 
track_1 = [
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
        'module_name': 'wait_balance', # Module Name
        'description': '(polygon_zkevm)', # Additional Module Description
        'params': {
            'chain': 'polygon_zkevm', # Network where we are awaiting coins
            'min_balance': 0.01, # Script proceeds to next module when balance exceeds this number
            'token': '', # Token address. Leave empty for native token
        },
    },
    {
        'module_name': 'sleeping', # Module Name
        'description': '(30-50s)', # Additional Module Description
        'params': {
            'from': 30, # Sleep duration starting from
            'to': 50, # Sleep duration up to
        },
    },
    {
        'module_name': 'rocketsam',
    }
]

# POLYGON_ZKEVM : exchange_withdraw (arbitrum) => zerius_refuel (arbitrum => polygon_zkevm) => rocketsam
track_2 = [
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
        'module_name': 'wait_balance', # Module Name
        'description': '(arbitrum)', # Additional Module Description
        'params': {
            'chain': 'arbitrum', # Network where we are awaiting coins
            'min_balance': 0.01, # Script proceeds to next module when balance exceeds this number
            'token': '', # Token address. Leave empty for native token
        },
    },
    {
        'module_name': 'sleeping', # Module Name
        'description': '(30-50s)', # Additional Module Description
        'params': {
            'from': 30, # Sleep duration starting from
            'to': 50, # Sleep duration up to
        },
    },
    {
        'module_name': 'zerius_refuel', # Module Name
        'description': '(arbitrum => polygon_zkevm)', # Additional Module Description
        'params': {
            'from_chain': ['arbitrum'], # From which network
            'to_chain': ['polygon_zkevm'], # To which network
            'amount_from': 0, # Refuel from a certain amount of coins
            'amount_to': 0, # Refuel up to a certain amount of coins
            'swap_all_balance': True, # True / False. If True, then refuel the entire balance
            'min_amount_swap': 0.003, # If the balance is less than this amount, no refuel will be made
            'keep_value_from': 0.0005, # How many coins to keep on the wallet (only works when: min_amount_swap = True)
            'keep_value_to': 0.001, # Up to how many coins to keep on the wallet (only works when: min_amount_swap = True)
        },
    },
    {
        'module_name': 'wait_balance', # Module Name
        'description': '(polygon_zkevm)', # Additional Module Description
        'params': {
            'chain': 'polygon_zkevm', # Network where we are awaiting coins
            'min_balance': 0.005, # Script proceeds to next module when balance exceeds this number
            'token': '', # Token address. Leave empty for native token
        },
    },
    {
        'module_name': 'sleeping', # Module Name
        'description': '(30-50s)', # Additional Module Description
        'params': {
            'from': 30, # Sleep duration starting from
            'to': 50, # Sleep duration up to
        },
    },
    {
        'module_name': 'rocketsam',
    },
]

# POLYGON_ZKEVM : okx_withdraw (arbitrum) => orbiter_bridge (arbiturm => polygon_zkevm) => rocketsam => orbiter_bridge (polygon_zkevm => arbitrum) => transfer (arbitrum)
track_3 = [
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
        'module_name': 'wait_balance', # Module Name
        'description': '(arbitrum)', # Additional Module Description
        'params': {
            'chain': 'arbitrum', # Network where we are awaiting coins
            'min_balance': 0.01, # Script proceeds to next module when balance exceeds this number
            'token': '', # Token address. Leave empty for native token
        },
    },
    {
        'module_name': 'sleeping', # Module Name
        'description': '(30-50s)', # Additional Module Description
        'params': {
            'from': 30, # Sleep duration starting from
            'to': 50, # Sleep duration up to
        },
    },
    {
        'module_name': 'orbiter_bridge', # Module Name
        'description': '(arbitrum => polygon_zkevm)', # Additional Module Description
        'params': {
            'from_chain': ['arbitrum'], # From which network
            'to_chain': ['polygon_zkevm'], # To which network
            'amount_from': 0, # Transfer from a certain amount of coins
            'amount_to': 0, # Transfer up to a certain amount of coins
            'bridge_all_balance': True, # True / False. If True, then transfer the entire balance
            'min_amount_bridge': 0.002, # If the balance is less than this amount, no transfer will be made
            'keep_value_from': 0.001, # How many coins to keep on the wallet (only works when: bridge_all_balance = True)
            'keep_value_to': 0.002, # Up to how many coins to keep on the wallet (only works when: bridge_all_balance = True)
        },
    },
    {
        'module_name': 'wait_balance', # Module Name
        'description': '(polygon_zkevm)', # Additional Module Description
        'params': {
            'chain': 'polygon_zkevm', # Network where we are awaiting coins
            'min_balance': 0.01, # Script proceeds to next module when balance exceeds this number
            'token': '', # Token address. Leave empty for native token
        },
    },
    {
        'module_name': 'sleeping', # Module Name
        'description': '(30-50s)', # Additional Module Description
        'params': {
            'from': 30, # Sleep duration starting from
            'to': 50, # Sleep duration up to
        },
    },
    {
        'module_name': 'rocketsam',
    },
    {
        'module_name': 'sleeping', # Module Name
        'description': '(30-50s)', # Additional Module Description
        'params': {
            'from': 30, # Sleep duration starting from
            'to': 50, # Sleep duration up to
        },
    },
    {
        'module_name': 'orbiter_bridge', # Module Name
        'description': '(polygon_zkevm => arbitrum)', # Additional Module Description
        'params': {
            'from_chain': ['polygon_zkevm'], # From which network
            'to_chain': ['arbitrum'], # To which network
            'amount_from': 0, # Transfer from a certain amount of coins
            'amount_to': 0, # Transfer up to a certain amount of coins
            'bridge_all_balance': True, # True / False. If True, then transfer the entire balance
            'min_amount_bridge': 0.005, # If the balance is less than this amount, no transfer will be made
            'keep_value_from': 0.003, # How many coins to keep on the wallet (only works when: bridge_all_balance = True)
            'keep_value_to': 0.005, # Up to how many coins to keep on the wallet (only works when: bridge_all_balance = True)
        },
    },
    {
        'module_name': 'wait_balance', # Module Name
        'description': '(arbitrum)', # Additional Module Description
        'params': {
            'chain': 'arbitrum', # Network where we are awaiting coins
            'min_balance': 0.01, # Script proceeds to next module when balance exceeds this number
            'token': '', # Token address. Leave empty for native token
        },
    },
    {
        'module_name': 'sleeping', # Module Name
        'description': '(30-50s)', # Additional Module Description
        'params': {
            'from': 30, # Sleep duration starting from
            'to': 50, # Sleep duration up to
        },
    },
    {
        'module_name': 'transfer', # Module Name
        'description': '(arbitrum)', # Additional Module Description
        'params': {
            'chain': 'arbitrum', # Network to withdraw to
            'token_address': '', # Leave empty if it's the native token of the network
            'amount_from': 0, # Transfer from a certain amount of coins
            'amount_to': 0, # Transfer up to a certain amount of coins
            'transfer_all_balance': True, # True / False. If True, then transfer the entire balance
            'min_amount_transfer': 0.003, # If the balance is less than this amount, no transfer will be made
            'keep_value_from': 0.001, # How many coins to keep on the wallet (only works when: transfer_all_balance = True)
            'keep_value_to': 0.003, # Up to how many coins to keep on the wallet (only works when: transfer_all_balance = True)
        },
    },
]


tracks = [
    track_1,
    track_2,
    track_3,
]

