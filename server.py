import asyncio
import aiohttp
import websockets
from datetime import datetime, timedelta
import platform
import json

test = [
    {
                "date":"01.12.2014","bank":"PB","baseCurrency":980,"baseCurrencyLit":"UAH","exchangeRate":
                [
                    {"baseCurrency":"UAH","currency":"EUR","saleRateNB":18.7949200,"purchaseRateNB":18.7949200,"saleRate":20.0000000,"purchaseRate":19.2000000},
                    {"baseCurrency":"UAH","currency":"PLZ","saleRateNB":4.4922010,"purchaseRateNB":4.4922010,"saleRate":5.0000000,"purchaseRate":4.2000000},
                    {"baseCurrency":"UAH","currency":"USD","saleRateNB":15.0564130,"purchaseRateNB":15.0564130,"saleRate":15.7000000,"purchaseRate":15.3500000},
                ]
            },
{
                "date":"02.12.2014","bank":"PB","baseCurrency":980,"baseCurrencyLit":"UAH","exchangeRate":
                [
                    {"baseCurrency":"UAH","currency":"EUR","saleRateNB":18.7949200,"purchaseRateNB":18.7949200,"saleRate":20.0000000,"purchaseRate":19.2000000},
                    {"baseCurrency":"UAH","currency":"PLZ","saleRateNB":4.4922010,"purchaseRateNB":4.4922010,"saleRate":5.0000000,"purchaseRate":4.2000000},
                    {"baseCurrency":"UAH","currency":"USD","saleRateNB":15.0564130,"purchaseRateNB":15.0564130,"saleRate":15.7000000,"purchaseRate":15.3500000}
                ]
            }


]

class Server:
    CURRENCY = ['EUR', 'USD', 'PLZ']
    URL_DATE = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='

    async def create_result(self, data):
        # print('DATA: ')
        # for el in data:
        #     print('------------------------')
        #     print(el)
        result =[]
        for element in data:
            row = {element['date']: {}}
            for currency in element['exchangeRate']:
                if currency['currency'] in self.CURRENCY:
                    row[element['date']][currency['currency']] = {
                        'saleNB': currency['saleRateNB'], 
                        'purshcaseNB': currency['purchaseRateNB'], 
                        'salePB': currency['saleRate'], 
                        'purshcasePB': currency['purchaseRate']
                    }
            result.append(row)
        
        # print(result)

        return json.dumps(result)

    async def get_currancy_for_date(self, session, date):
        try:
            async with session.get(f'{self.URL_DATE}{date}') as response:
                if response.status == 200:
                    res = await response.json()
                    return res
                else:
                    print(f'Error status {response.status} for {self.URL_DATE}{date}')
        except aiohttp.ClientConnectionError as e:
            print(f'Connection error: {self.URL_DATE}{date}', str(e))

    async def get_currency(self, count_day):
        today = datetime.now()
        res_list = []
        async with aiohttp.ClientSession() as session:
            res_list = [asyncio.create_task(self.get_currancy_for_date(session, (today - timedelta(i)).strftime('%d.%m.%Y'))) for i in range(int(count_day))]
            res = await asyncio.gather(*res_list, return_exceptions=True)
            return res

    async def send_to_client(self, data, ws):
        count_days = 1
        args = data.split(' ')
        if len(args) > 2:
            await ws.send('Wrong arguments! Please send number of days.')
            return 'Ok'
        try:
            count_days = int(args[1])
        except:
            await ws.send('Wrong arguments! Please send number of days.')
            return 'Ok'
        res = await self.get_currency(count_days)
        data_client = await self.create_result(res)
        await ws.send(data_client)

    async def run_server(self, ws):
        data = await ws.recv()
        await self.send_to_client(data, ws)

async def main():
    server = Server()
    async with websockets.serve(server.run_server, 'localhost', 5000):
        await asyncio.Future()

if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())