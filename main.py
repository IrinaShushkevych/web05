import asyncio
import aiohttp
from datetime import datetime, timedelta
import platform
import sys

CURRENCY = ['EUR', 'USD']
URL_DATE = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='

def print_result(res):
    col_width = 20
    width = col_width + len(CURRENCY)*col_width
    print('-'*width) 
    string = '| {:^' + str(col_width - 3) + '} |'
    for _ in range(len(CURRENCY)):
        string += ' {:^' + str(col_width - 3) + '} |'
    print(string.format('', *CURRENCY))
    print('-'*width) 
    for element in res:
        row = [['', element['date'], '', '']]
        for currency in element['exchangeRate']:
            if currency['currency'] in CURRENCY:
                row.append([
                    'NB ' + str(currency['saleRateNB']), 
                    'NB ' + str(currency['purchaseRateNB']), 
                    'PB ' + str(currency['saleRate']), 
                    'PB ' + str(currency['purchaseRate'])
                    ])
        for i in range(4):
            print(string.format(*[el[i] for el in row]))
        print('-'*width) 
    
async def get_currancy_for_date(session, date):
    try:
        async with session.get(f'{URL_DATE}{date}') as response:
            if response.status == 200:
                res = await response.json()
                return res
            else:
                print(f'Error status {response.status} for {URL_DATE}{date}')
    except aiohttp.ClientConnectionError as e:
        print(f'Connection error: {URL_DATE}{date}', str(e))

async def get_currency(count_day):
    today = datetime.now()
    res_list = []
    async with aiohttp.ClientSession() as session:
        res_list = [asyncio.create_task(get_currancy_for_date(session, (today - timedelta(i)).strftime('%d.%m.%Y'))) for i in range(int(count_day))]
        res = await asyncio.gather(*res_list, return_exceptions=True)
        return res

async def main():
    count_days = 1
    args = sys.argv
    if len(args) > 2:
        print('Wrong arguments! Please send number of days.')
    try:
        count_days = int(args[1])
    except:
        print('Wrong arguments! Please send number of days.')
    res = await get_currency(count_days)
    print_result(res)

if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

