import sys
import platform
import asyncio
import logging

import aiohttp

URL = 'https://api.privatbank.ua/p24api/exchange_rates?date=01.12.2014'
DATE_LIMIT = 10


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


async def parse_response(url=URL, rule='base'):
    list_currency = []
    response = await request(URL)
    if response:
        list_currency.append(f'Date: {response.get("date")} (NB in UAH)')
        exchange_rates = response.get("exchangeRate")
        for el in exchange_rates:
            list_currency.append("{:<5}| buy: {:<10}|sale: {:<10}|".format(el.get("currency"),
                                                                           el.get("purchaseRateNB"),
                                                                           el.get("saleRateNB")))

    return '\n'.join(list_currency)


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    #asyncio.run(main())
    r = asyncio.run(parse_response())
    print(r)