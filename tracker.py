import argparse
from web3 import Web3

ERC20_ABI = '''
[
    {"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},
    {"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":
    [{"name":"balance","type":"uint256"}],"type":"function"},
    {"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"}
]
'''

def get_balance(rpc_url, token_address, wallet_address):
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.isConnected():
        print("Error: Could not connect to RPC.")
        return

    token = w3.eth.contract(address=w3.toChecksumAddress(token_address), abi=ERC20_ABI)
    symbol = token.functions.symbol().call()
    decimals = token.functions.decimals().call()
    balance = token.functions.balanceOf(w3.toChecksumAddress(wallet_address)).call()
    human_balance = balance / (10 ** decimals)
    print(f"{wallet_address} has {human_balance} {symbol}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ERC20 Token Balance Checker")
    parser.add_argument("--rpc", required=True, help="Ethereum RPC URL")
    parser.add_argument("--token", required=True, help="ERC-20 token contract address")
    parser.add_argument("--wallet", required=True, help="Wallet address to check balance")
    args = parser.parse_args()
    get_balance(args.rpc, args.token, args.wallet)
