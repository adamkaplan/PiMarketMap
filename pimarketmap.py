#!/usr/bin/python
# vim: noai:ts=4:sw=4:expandtab

import asyncio
import base64
import collections
from enum import Enum
import json
import quotefeedprovider_pb2
import requests
import ssl
import sys
import signal
import time
from typing import Tuple
import websockets

try:
    import unicornhat as unicorn
    print("Unicorn pHAT detected")
except ImportError:
    print("No Unicorn pHAT detected, using simulator")
    from unicorn_hat_sim import unicornphat as unicorn


# Install control-c handler & clear grid
def signal_handler(sig, frame):
    print('Exiting.')
    unicorn.clear()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


ALL_FIELDS = [
    'regularMarketPrice',
    'regularMarketChangePercent',
    #'regularMarketChange',
    #'regularMarketOpen',
    #'regularMarketPreviousClose',
    'marketCap'
]

QUOTE = quotefeedprovider_pb2.PricingData()

class Color:
    # Flash Colors
    negative = (128, 0, 0)
    positive = (0, 128, 0)
    neutral  = (0, 0, 128)

    # Persistant Colors
    flash_negative = (255, 0, 0)
    flash_positive = (0, 255, 0)
    flash_neutral  = (0, 0, 255)

    def colorForChange(change: float) -> Tuple[int, int, int]:
        if change < -0.0005:
            return Color.negative
        elif change > 0.0005:
            return Color.positive
        else:
            return Color.neutral

    def flashColorForChange(change: float) -> Tuple[int, int, int]:
        if change < 0:
            return Color.flash_negative
        elif change > 0:
            return Color.flash_positive
        else:
            return Color.flash_neutral


class Component:
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.index = 0
        self.quote = dict()


class ComponentList(collections.MutableSequence):

    class SortKey(Enum):
        MARKET_CAP = 'market_cap'
        CHANGE_PERCENT = 'change_percent'

    def sort(self, sort_key: SortKey):
        self.sort_key = sort_key
        self.list.sort(key=lambda x: x.quote[sort_key.value], reverse=True)
        for idx,component in enumerate(self.list):
            component.index = idx

    def check(self, v):
        if not isinstance(v, Component):
            raise TypeError('Must be a Component type')

    def find(self, symbol: str) -> Component:
        return self.lookup_table[symbol]

    def __init__(self, *args):
        self.list = list()
        self.lookup_table = dict()
        self.sort_key = None
        self.extend(list(args))

    def __len__(self): return len(self.list)

    def __getitem__(self, i): return self.list[i]

    def __delitem__(self, i):
        if i in self.list:
            del self.lookup_table[self.list[i].symbol]
        del self.list[i]

    def __setitem__(self, i, v):
        self.check(v)
        v.index = i
        self.list[i] = v
        self.lookup_table[v.symbol] = v

    def insert(self, i, v):
        self.check(v)
        v.index = i
        self.list.insert(i, v)
        self.lookup_table[v.symbol] = v

    def __str__(self):
        return str(self.list)



class Renderer:

    def __init__(self, unicorn: unicorn):
        self.phat = unicorn
        self.width, self.height = unicorn.get_shape()
        print('pHAT dimensions %d x %d' % (self.width, self.height))

    def _set_pixel(self, component: Component, color: Tuple[int,int,int]) -> None:
        idx = component.index
        y = int(idx / self.width)
        x = self.width - 1 - (idx % self.width) # invert for top-to-bottom
        #print('> pHAT pixel set at %d x %d' % (x, y))
        self.phat.set_pixel(x, y, color[0], color[1], color[2])
        self.phat.show() 

    def flash(self, components: list) -> None:
        for component in components:
            quote = component.quote
            diff = quote['last_change_percent'] - quote['change_percent'] 
            if diff == 0:
                continue
            #print('Flashing %s' % component.symbol)
            color = Color.flashColorForChange(diff)
            self._set_pixel(component, color)

    def deflash(self, components: list):
        for component in components:
            #print('Deflashing %s' % component.symbol)
            color = Color.colorForChange(component.quote['change_percent'])
            self._set_pixel(component, color)

    def render(self, components: list) -> None:
        for component in components:
            color = Color.colorForChange(component.quote['change_percent'])
            self._set_pixel(component, color)
            time.sleep(0.005)

class Streamer:

    def __init__(self, renderer: Renderer, components: ComponentList):
        self.renderer = renderer
        self.components = components

    async def connect(self) -> None:
        async with websockets.client.connect('wss://streamer.finance.yahoo.com', ssl=True) as websocket:
            tickers = [q.symbol for q in self.components]
            message = json.dumps({ 'subscribe': tickers })
            print("Subscribing to quote streamer...")
            print(message)
            await websocket.send(message)

            print("Spawning listener...")
            update_symbols = set()
            await asyncio.gather(
                self.receiveMessage(websocket, update_symbols),
                self.processUpdates(update_symbols)
            )

    async def receiveMessage(self, websocket, update_symbols: list) -> None:
        while True:
            msg = await websocket.recv()
            raw = base64.b64decode(msg)
            parsed = QUOTE.FromString(raw)
            self._streamingUpdate(parsed, update_symbols)

    async def processUpdates(self, update_symbols: set) -> None:
        pending_deflash = dict()

        while True:
            await asyncio.sleep(0.05)
            if len(update_symbols) == 0:
                continue

            if self.components.sort_key == ComponentList.SortKey.MARKET_CAP:
                # Render the update flash
                to_update = map(lambda s: self.components.find(s), update_symbols)
                self.renderer.flash(to_update)

            now = time.time()

            # De-flash old updates now
            symbols = self._components_to_deflash(pending_deflash, now)
            comps = map(lambda s: self.components.find(s), symbols)
            self.renderer.deflash(comps)

            # Set the updates to de-flash later
            deflash_at = now + 0.75
            for s in update_symbols:
                pending_deflash[s] = deflash_at

            # Clear the updates list of processed updates
            update_symbols.clear()

    def _components_to_deflash(self, pending_deflash: dict, time_limit: float) -> list:
        to_deflash = [s for s,t in pending_deflash.items() if t <= time_limit]
        for symbol in to_deflash:
            del pending_deflash[symbol]
        return to_deflash

    def _streamingUpdate(self, quote: Component, update_symbols: list):
        component = self.components.find(quote.id)
        quoteDict = component.quote
        if not quoteDict:
            return

        if quote.HasField('change_percent'):
            if (not 'last_change_percent' in quoteDict) or quoteDict['last_change_percent'] != quote.change_percent:
                quoteDict['last_change_percent'] = quoteDict['change_percent']
                quoteDict['change_percent'] = quote.change_percent
                update_symbols.add(quote.id)

        if quote.HasField('marketcap'):
            quoteDict['market_cap'] = quote.marketcap


def fetchQuotes(tickers: list, fields: list = ALL_FIELDS) -> list:
    ticker_str = ','.join(tickers)
    fields_str = ','.join(fields)
    url = 'https://mobile-query.finance.yahoo.com/v6/finance/quote/?symbols=%s&fields=%s' % (ticker_str, fields_str)
    headers = {'user-agent': 'PiMarketMap/1.0.0'}
    res = requests.get(url, headers=headers, timeout=5)
    j = res.json()
    return j['quoteResponse']['result']


async def rotateLayout(renderer: Renderer, components: ComponentList):
    sort_keys = list(ComponentList.SortKey)
    while True:
        await asyncio.sleep(8.0)
        idx = sort_keys.index(components.sort_key)
        next_idx = (idx + 1) % len(sort_keys)
        next_sort = sort_keys[next_idx]
        components.sort(next_sort)
        print("Changing sort to %s" % next_sort.value)
        renderer.render(components)


def main():
    unicorn.set_layout(unicorn.PHAT)
    unicorn.rotation(90)
    unicorn.brightness(0.4)

    renderer = Renderer(unicorn)

    # Fetch the Dow Jones Industrial Average list of 30 components
    dow = fetchQuotes(['^DJI'], ['components'])
    dow30_tickers = dow[0]['components']
    # There are 32 pixels, so add 2 more items
    dow30_tickers.append('AMZN')
    dow30_tickers.append('FB')

    print("Fetching Dow 30, and 2 more: %s" % dow30_tickers)
    dow_30 = fetchQuotes(dow30_tickers)

    components = ComponentList()
    for quote in dow_30:
        change = quote['regularMarketChangePercent'] if 'regularMarketChangePercent' in quote else 0
        mktCap = quote['marketCap'] if 'marketCap' in quote else 0

        print("%s: %f %d" % (quote['symbol'], change, mktCap))
        comp = Component(quote['symbol'])
        comp.quote = {
            'change_percent': change,
            'market_cap': mktCap
        }
        components.append(comp)

    components.sort(ComponentList.SortKey.MARKET_CAP)
    renderer.render(components)
    streamer = Streamer(renderer, components)

    asyncio.get_event_loop().run_until_complete(asyncio.gather(
        #rotateLayout(renderer, components),
        streamer.connect()
    ))

if __name__ == '__main__':
    main()

#    c1 = Component('GBPUSD=X')
#    c2 = Component('JPY=X')
#    c3 = Component('BTC-USD')
#    components[0] = c1
#    components[1] = c2
#    components[2] = c3
#    c1.quote = {
#        'change_percent': 0,
#        'market_cap': 0
#    }
#    c2.quote = {
#        'change_percent': 0,
#        'market_cap': 0
#    }
#    c3.quote =  {
#        'change_percent': 0,
#        'market_cap': 0
#    }
