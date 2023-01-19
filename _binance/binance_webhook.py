# BinanceSocketManager. 
# User Socket. 
# This watches for 3 different user events

import os
import asyncio
from binance import BinanceSocketManager
from binance.client import AsyncClient
from dotenv import load_dotenv

load_dotenv()


BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', None)
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', None)


class BinancePayment:
    def __init__(self, async_client: AsyncClient = None):
        self._async_client = async_client

    async def run(self, loop):
        loop.create_task(self._user_account_listener())

    async def _user_account_listener(self):
        bsm = BinanceSocketManager(self._async_client)
        # async with bsm.trade_socket(symbol='BTCUSDT') as us: # USE FOR TESTING
        async with bsm.user_socket() as us:
            while True:
                msg = await us.recv()
                print('_user_account_listener ', msg)


async def main():
    async_client = await AsyncClient().create(
        api_key=BINANCE_API_KEY, 
        api_secret=BINANCE_SECRET_KEY
    )

    binance_payment = BinancePayment(async_client)
    loop.create_task(binance_payment.run(loop))

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
    