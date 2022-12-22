import asyncio
import aiohttp
from datetime import datetime, timedelta
import platform
import sys

test = [
    {
                "date":"01.12.2014","bank":"PB","baseCurrency":980,"baseCurrencyLit":"UAH","exchangeRate":
                [
                    {"baseCurrency":"UAH","currency":"CHF","saleRateNB":15.6389750,"purchaseRateNB":15.6389750,"saleRate":17.0000000,"purchaseRate":15.5000000},
                    {"baseCurrency":"UAH","currency":"EUR","saleRateNB":18.7949200,"purchaseRateNB":18.7949200,"saleRate":20.0000000,"purchaseRate":19.2000000},
                    {"baseCurrency":"UAH","currency":"GBP","saleRateNB":23.6324910,"purchaseRateNB":23.6324910,"saleRate":25.8000000,"purchaseRate":24.0000000},
                    {"baseCurrency":"UAH","currency":"PLN","saleRateNB":4.4922010,"purchaseRateNB":4.4922010,"saleRate":5.0000000,"purchaseRate":4.2000000},
                    {"baseCurrency":"UAH","currency":"SEK","saleRateNB":2.0283750,"purchaseRateNB":2.0283750},
                    {"baseCurrency":"UAH","currency":"UAH","saleRateNB":1.0000000,"purchaseRateNB":1.0000000},
                    {"baseCurrency":"UAH","currency":"USD","saleRateNB":15.0564130,"purchaseRateNB":15.0564130,"saleRate":15.7000000,"purchaseRate":15.3500000},
                    {"baseCurrency":"UAH","currency":"XAU","saleRateNB":17747.7470000,"purchaseRateNB":17747.7470000},
                    {"baseCurrency":"UAH","currency":"CAD","saleRateNB":13.2107400,"purchaseRateNB":13.2107400,"saleRate":15.0000000,"purchaseRate":13.0000000}
                ]
            },
            {
                "date":"02.12.2014","bank":"PB","baseCurrency":980,"baseCurrencyLit":"UAH","exchangeRate":
                [
                    {"baseCurrency":"UAH","currency":"CHF","saleRateNB":15.6389750,"purchaseRateNB":15.6389750,"saleRate":17.0000000,"purchaseRate":15.5000000},
                    {"baseCurrency":"UAH","currency":"EUR","saleRateNB":18.7949200,"purchaseRateNB":18.7949200,"saleRate":20.0000000,"purchaseRate":19.2000000},
                    {"baseCurrency":"UAH","currency":"GBP","saleRateNB":23.6324910,"purchaseRateNB":23.6324910,"saleRate":25.8000000,"purchaseRate":24.0000000},
                    {"baseCurrency":"UAH","currency":"PLN","saleRateNB":4.4922010,"purchaseRateNB":4.4922010,"saleRate":5.0000000,"purchaseRate":4.2000000},
                    {"baseCurrency":"UAH","currency":"SEK","saleRateNB":2.0283750,"purchaseRateNB":2.0283750},
                    {"baseCurrency":"UAH","currency":"UAH","saleRateNB":1.0000000,"purchaseRateNB":1.0000000},
                    {"baseCurrency":"UAH","currency":"USD","saleRateNB":15.0564130,"purchaseRateNB":15.0564130,"saleRate":15.7000000,"purchaseRate":15.3500000},
                    {"baseCurrency":"UAH","currency":"XAU","saleRateNB":17747.7470000,"purchaseRateNB":17747.7470000},
                    {"baseCurrency":"UAH","currency":"CAD","saleRateNB":13.2107400,"purchaseRateNB":13.2107400,"saleRate":15.0000000,"purchaseRate":13.0000000}
                ]
            }
]

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
        for curr in CURRENCY:
            add = False
            for currency in element['exchangeRate']:
                if currency['currency'] == curr:
                    row.append([
                        'NB ' + str(currency['saleRateNB']), 
                        'NB ' + str(currency['purchaseRateNB']), 
                        'PB ' + str(currency['saleRate']), 
                        'PB ' + str(currency['purchaseRate'])
                        ])
                    add = True
            if not add:
                row.append(['', '', '', ''])
        print(row)
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
    if len(args) >= 1:
        try:
            count_days = int(args[1])
            if count_days > 10:
                count_days = 10
        except:
            print('Wrong arguments! Please send number of days.')
    if len(args) > 2:
        for el in args[2:]:
            CURRENCY.append(el.upper())
    res = await get_currency(count_days)
    print_result(res)

if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

