import sys
import platform
import asyncio
import logging
from datetime import date, timedelta, datetime

import aiohttp

URL = 'https://api.privatbank.ua/p24api/exchange_rates?date='
RULE = {'aud': 'AUD', 'cad': 'CAD', 'czk': 'CZK', 'dkk': 'DKK',
        'huf': 'HUF', 'ils': 'ILS', 'jpy': 'JPY', 'lvl': 'LVL',
        'ltl': 'LTL', 'nok': 'NOK', 'skk': 'SKK', 'sek': 'SEK',
        'chf': 'CHF', 'gbp': 'GBP', 'usd': 'USD', 'byr': 'BYR',
        'eur': 'EUR', 'gel': 'GEL', 'plz': 'PLZ',
        'base': ['USD', 'EUR'],
        'all': ['AUD', 'CAD', 'CZK', 'DKK', 'HUF', 'ILS', 'JPY',
                'LVL', 'LTL', 'NOK', 'SKK', 'SEK', 'CHF', 'GBP',
                'USD', 'BYR', 'EUR', 'GEL', 'PLZ']}
DATE_LIMIT = 10
MANUAL = '''
Apps print currency exchange today with base rule (usd & eur) if no any arguments
Choose currency like this               - input "main.py usd" 
Choose all currency                     - input "main.py all"
Apps print currency exchange in period from 1 to 10 days in base rule (usd & eur)
Currency today                          - input "main.py" or "main.py 0", "main.py 1"
Currency today and yesterday            - input "main.py 2"
Currency from today to 9 days ago       - input "main.py 10"
input more than 10 days ago return only last 10 days
Currency usd from today to 9 days ago   - input "main.py 10 usd" or "main.py usd 10"'''


async def request(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    res = await response.json()
                    return res
                logging.error(f'Error status {response.status} for {url}')
        except aiohttp.ClientConnectionError as e:
            logging.error(f'Connection error {url}: {e}')
        return None


async def day_response(url=URL, rule='base'):
    url = f'{url}01.12.2014'
    list_currency = []
    response = await request(url)
    if response:
        list_currency.append(f'Date: {response.get("date")} (NB in UAH)')
        exchange_rates = response.get("exchangeRate")
        if rule in RULE:
            for el in exchange_rates:
                if el.get("currency") in RULE.get(rule):
                    list_currency.append("{:<5}| buy: {:<10}|sale: {:<10}|".format(el.get("currency"),
                                                                                   el.get("purchaseRateNB"),
                                                                                   el.get("saleRateNB")))
        else:
            list_currency.append(f'Currency {rule} not found. Input "main.py help" for more information.')

    return '\n'.join(list_currency)


def link_list(days: int) -> list:
    res_list = []
    for i in range(int(days)):
        date_res = date.today() - timedelta(days=i)
        str_res = date_res.strftime('%d.%m.%Y')
        res_list.append(f'{URL}{str_res}')
    return res_list


def manual():
    print(MANUAL)
    print('Available currency:')
    print([i for i in RULE][:-2])
    print("Additional currency command :['all', 'base']")


def input_parser():
    list_parse = sys.argv[1:]


if __name__ == '__main__':
    # manual()
    start = datetime.now()
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r = asyncio.run(day_response())
    print(r)
    t = datetime.now() - start
    print(t.microseconds/1000000 )
