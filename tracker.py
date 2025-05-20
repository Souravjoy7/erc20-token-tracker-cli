import argparse
import requests
from web3 import Web3

ERC20_ABI = '''
[
    {"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},
    {"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"},
    {"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"}
]
'''

def get_token_info(w3, token_address, wallet):
    token = w3.eth.contract(address=w3.toChecksumAddress(token_address), abi=ERC20_ABI)
    symbol = token.functions.symbol().call()
    decimals = token.functions.decimals().call()
    raw_balance = token.functions.balanceOf(w3.toChecksumAddress(wallet)).call()
    balance = raw_balance / (10 ** decimals)
    return symbol, balance

def get_prices(symbols):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(symbols)}&vs_currencies=usd"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {}

def symbol_to_coingecko_id(symbol):
    mapping = {
        'DAI': 'dai',
        'USDC': 'usd-coin',
        'USDT': 'tether',
        'WBTC': 'wrapped-bitcoin',
        'WETH': 'weth',
        'LINK': 'chainlink'
    }
    return mapping.get(symbol.upper(), None)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rpc", required=True, help="Ethereum RPC URL")
    parser.add_argument("--wallet", required=True, help="Wallet address")
    parser.add_argument("--tokens", required=True, nargs='+', help="List of token contract addresses")
    args = parser.parse_args()

    w3 = Web3(Web3.HTTPProvider(args.rpc))
    if not w3.isConnected():
        print("Error: Could not connect to RPC.")
        return

    total_usd = 0
    token_data = []

    for token_address in args.tokens:
        try:
            symbol, balance = get_token_info(w3, token_address, args.wallet)
            coingecko_id = symbol_to_coingecko_id(symbol)
            usd_price = 0

            if coingecko_id:
                price_data = get_prices([coingecko_id])
                usd_price = price_data.get(coingecko_id, {}).get("usd", 0)

            usd_value = balance * usd_price
            total_usd += usd_value

            token_data.append((symbol, balance, usd_value))
        except Exception as e:
            print(f"Error with token {token_address}: {str(e)}")

    print(f"\nBalances for {args.wallet}:\n")
    for sym, bal, usd in token_data:
        print(f"{sym:<8}: {bal:,.4f} (${usd:,.2f})")
    print(f"\nTotal USD: ${total_usd:,.2f}")

if __name__ == "__main__":
    main()
