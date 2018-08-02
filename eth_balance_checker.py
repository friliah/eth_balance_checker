import pprint
import sys
import textwrap
import time

# pip install https://github.com/guillelo11/ethplorer-py/archive/master.zip
from ethplorer.address import Address
from tabulate import tabulate

#responce
"""{
    address: # address,
    ETH: {   # ETH specific information
        balance:  # ETH balance
        totalIn:  # Total incoming ETH value
        totalOut: # Total outgoing ETH value
    },
    contractInfo: {  # exists if specified address is a contract
       creatorAddress:  # contract creator address,
       transactionHash: # contract creation transaction hash,
       timestamp:       # contract creation timestamp
    },
    tokenInfo:  # exists if specified address is a token contract address (same format as token info),
    tokens: [   # exists if specified address has any token balances
        {
            tokenInfo: # token data (same format as token info),
            balance:   # token balance (as is, not reduced to a floating point value),
            totalIn:   # total incoming token value
            totalOut:  # total outgoing token value
        },
        ...
    ],
    countTxs:    # Total count of incoming and outcoming transactions (including creation one),
}"""


non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
checked_addresses = {}
checked_counter = 0


def get_current_tokens_list(total_dict):
    current_tokens_list= []
    for token in total_dict['tokens']:
        current_tokens_list.append(token['tokenInfo']['address'])
    return current_tokens_list


def get_total_balance_dict(list_of_dicts):
    resulting_dict = {
    'ETH': {   
            'balance': 0,
            'wallets_with_balance': {}#contains wallet:balance key pairs
    },
    'tokens': []  # exists if specified address has any token balances
    }
    for d in list_of_dicts:
        resulting_dict['ETH']['balance'] = resulting_dict['ETH']['balance'] + d['ETH']['balance']
        if d['ETH']['balance'] != 0:
            resulting_dict['ETH']['wallets_with_balance'][d['address']] = d['ETH']['balance']
        if 'tokens' in d:
            current_tokens_list = get_current_tokens_list(resulting_dict)
            for token in d['tokens']:
                if token['tokenInfo']['address'] in current_tokens_list:
                    for res_token in resulting_dict['tokens']:
                        if token['tokenInfo']['address'] == res_token['tokenInfo']['address']:
                            res_token['balance'] = res_token['balance'] + token['balance']
                            res_token['wallets_with_balance'][d['address']] = token['balance']
                            break
                else:
                    resulting_dict['tokens'].append(token)
                    resulting_dict['tokens'][-1]['wallets_with_balance'] = {}
                    resulting_dict['tokens'][-1]['wallets_with_balance'][d['address']] = token['balance']
    return resulting_dict


def get_addresses(filepath):
    try:
        with open(filepath, 'r') as fin:
            raw_data = fin.read().strip()
            if not raw_data:
                return None
            data = raw_data.splitlines()
            return data
    except IOError:
        return None


def print_wallet_balance(address_dict):
    print('ETH balance', address_dict['ETH']['balance'])
    print('#'*20)
    print('\nTokens\n')
    for token in address_dict['tokens']:
        token_balance = float(token['balance'])/(10**int(token['tokenInfo']['decimals']))
        usd_price = '-' if not token['tokenInfo']['price'] else float(token['tokenInfo']['price']['rate'])
        usd_balance = '-' if not token['tokenInfo']['price'] else usd_price*token_balance
        print('\n{} ({}) balance: {} tokens, {} USD, rate {} USD'.format(
            token['tokenInfo']['name'].translate(non_bmp_map),
            token['tokenInfo']['symbol'].translate(non_bmp_map),
            token_balance,
            usd_balance,
            usd_price ))


def print_table_wallet_balance(address_dict):
    print('\n'*3)
    print('#'*50)
    print('#'*50)
    print('ETH balance', address_dict['ETH']['balance'])
    print('#'*20)
    print('\nTokens\n')
    table = []
    headers = ['Token', 'Symbol', 'T Balance', 'USD Balance', 'USD Rate']
    for token in sorted(address_dict['tokens'], key=lambda x: (x['tokenInfo']['name'])):
        token_balance = float(token['balance'])/(10**int(token['tokenInfo']['decimals']))
        usd_price = '-' if not token['tokenInfo']['price'] else float(token['tokenInfo']['price']['rate'])
        usd_balance = '-' if not token['tokenInfo']['price'] else round(usd_price*token_balance, 2)
        table.append([
            textwrap.fill(token['tokenInfo']['name'].translate(non_bmp_map), width=20),
            token['tokenInfo']['symbol'].translate(non_bmp_map),
            token_balance,
            usd_balance,
            usd_price ])
    print(tabulate(table, headers, tablefmt="fancy_grid"))


def print_wallets_with_balance(total_balance_dict):
    print('\n'*4)
    print('#'*20)
    print('ETH balance:', total_balance_dict['ETH']['balance'])
    for wallet in total_balance_dict['ETH']['wallets_with_balance']:
        print(wallet,':', total_balance_dict['ETH']['wallets_with_balance'][wallet])
    print('#'*20,'\n')
    
    for token in sorted(total_balance_dict['tokens'], key=lambda x: (x['tokenInfo']['name'])):
        print(token['tokenInfo']['name'].translate(non_bmp_map), 'balance:',
              float(token['balance'])/(10**int(token['tokenInfo']['decimals'])))
        for wallet in token['wallets_with_balance']:
            print(wallet,':',
                  float(token['wallets_with_balance'][wallet])/(10**int(token['tokenInfo']['decimals'])))
        print('#'*20,'\n')


def get_balance_response(address):
    """return dict with response or none if bad response"""
    call = Address(address=address)
    response = call.get_address_info()
    if response:
        return response
    else:
        return None


def print_nonzero_balance_response(response):
    eth_balance = response['ETH']['balance']
    if eth_balance > 0:
        print('#'*10, response['address'])
        print('eth_balance',eth_balance)
    if 'tokens' in response:
        print('#'*10, response['address'])
        for token in response['tokens']:
            print(token['tokenInfo']['name'].translate(non_bmp_map), token['tokenInfo']['symbol'].translate(non_bmp_map), float(token['balance'])/(10**int(token['tokenInfo']['decimals'])))


def recursive_check_addresses(addresses_list,START_TIME, show_individual_wallet_balance, total_addresses, iteration=0):
    if len(addresses_list) == 0:
        print('end of recursion')
        return
    print('iteration', iteration)
    print('addresses to ckeck',len(addresses_list))
    #dict w key = address and value = response
    global checked_addresses
    global checked_counter
    addresses_check_later = []
    for number, address in enumerate(addresses_list):
        try:
            balance_response = get_balance_response(address)
            if balance_response:
                checked_counter += 1
                print('#'*10,checked_counter,'out of', total_addresses,'iteration', iteration)
                print(int(time.time()-START_TIME), 'seconds')
                if show_individual_wallet_balance:
                    print_nonzero_balance_response(balance_response)
                    print('#'*50,'\n\n')
                checked_addresses[address] = balance_response
            else:
                addresses_check_later.append(address)
        except Exception as e:
            print(e, address)
            addresses_check_later.append(address)
    iteration += 1
    recursive_check_addresses(addresses_check_later,START_TIME, show_individual_wallet_balance,total_addresses, iteration)

def get_transactions(address):
    call = Address(address=address)
    response = call.get_address_transactions()
    print('#'*10, response)


def main(addresses_file='addresses.txt',last=None, show_individual_wallet_balance = True):
    START_TIME = time.time()
    raw_addresses = get_addresses(addresses_file)
    #get unique values preserving (3.6+) the order
    addresses = list(dict.fromkeys(raw_addresses))[:last]
    total_addresses_qty = len(addresses)
    print('total_addresses_qty',total_addresses_qty, '\n')
    recursive_check_addresses(addresses, START_TIME, show_individual_wallet_balance=show_individual_wallet_balance,
                              total_addresses=total_addresses_qty)
    global checked_addresses
    total_balance_dict = get_total_balance_dict(list(checked_addresses.values()))
    print_table_wallet_balance(total_balance_dict)
    print_wallets_with_balance(total_balance_dict)


if __name__ == '__main__':
    main('wallets.txt',last=None, show_individual_wallet_balance = False)
    input('Press Enter to exit:\n')
    #address= ''
    #print(get_transactions(address))
