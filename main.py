import sys
import platform
import asyncio
import logging
from datetime import date, timedelta
from time import time

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


def response_parse(response: dict, rule='base') -> str:
    list_currency = []
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


async def iterator_req(link_urls):
    for url in link_urls:
        yield request(url)


async def run(iter_req):
    result = []
    async for req in iter_req:
        result.append(req)
    return await asyncio.gather(*result)


def link_list(days: int) -> list:
    res_list = []
    for i in range(int(days)):
        date_res = date.today() - timedelta(days=i)
        str_res = date_res.strftime('%d.%m.%Y')
        res_list.append(f'{URL}{str_res}')
    return res_list


def manual() -> None:
    print(MANUAL)
    print('Available currency:')
    print([i for i in RULE][:-2])
    print("Additional currency command :['all', 'base']")


def correcting_day(days: int) -> int:
    if days < 0:
        print(f'Days not be negative: {days}')
        days = 1
    elif days == 0 or days == 1:
        days = 1
    elif days > 10:
        days = 10
    return days


def input_parser() -> (int, str):
    list_parse = sys.argv[1:]
    days = 1
    rule = 'base'
    if len(list_parse) > 2:
        print(f'Too many arguments: {list_parse}')
    elif len(list_parse) == 2:
        if list_parse[0].strip().isdigit():
            days = int(list_parse[0].strip())
            days = correcting_day(days)
            if list_parse[1].strip().lower() in RULE:
                rule = list_parse[1].strip().lower()
            else:
                print(f'Currency for {days} days, but not found rule: {list_parse[1].strip().lower()}')
        elif list_parse[0].strip().lower() in RULE:
            rule = list_parse[0].strip().lower()
            if list_parse[1].strip().isdigit():
                days = int(list_parse[1].strip())
                days = correcting_day(days)
            else:
                print(f'Currency rule: {rule}, but days not found: {list_parse[1].strip().lower()}')
        else:
            print(f'These arguments not found: {list_parse[0].strip().lower()}, {list_parse[1].strip().lower()}')
    elif len(list_parse) == 1:
        if list_parse[0].strip().isdigit():
            days = int(list_parse[0].strip())
            days = correcting_day(days)
        elif list_parse[0].strip().lower() in RULE:
            rule = list_parse[0].strip().lower()
        elif list_parse[0].strip().lower() == 'help':
            manual()
        else:
            print(f'Not found rule: {list_parse[0].strip().lower()}')
    elif len(list_parse) == 0:
        print('Run app with argument "help": "main.py help" for more info.')
    return days, rule


def main():
    days, rule = input_parser()
    urls = link_list(days)
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r = asyncio.run(run(iterator_req(urls)))
    for day_res in r:
        print(response_parse(day_res, rule))


if __name__ == '__main__':
    start = time()
    main()
    t = time() - start
    print(f'Completed in {t} sec. Thanks for using.')
