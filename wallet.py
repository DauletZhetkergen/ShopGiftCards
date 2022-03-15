import requests

wallet_id = 'btc-c9839e3a4411aa5fdd8c90fa2795f474'
key = 'uwmvNVE0GP5ups4s0oIQxdE6VQblWYut'


def create_address():
    res = requests.post('https://apirone.com/api/v2/wallets/{}/addresses'.format(wallet_id))
    return res.json()['address']

def converter_btc(price):
    res = requests.post('https://blockchain.info/tobtc?currency=USD&value={}'.format(price))
    price_btc = '{0:f}'.format(res.json())
    return price_btc


def check_payment_btc(address):
    url = requests.get('https://apirone.com/api/v2/wallets/{}/addresses/{}'.format(wallet_id,address))
    available_balance = url.json()['balance']['available']
    return int(available_balance)

