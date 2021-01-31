import threading
import time
import util
import ccxt
import websocket
import json
import logging


class CustomBinance(ccxt.binance):

    def __init__(self, config={}):
        super(ccxt.binance, self).__init__(config)
        self.__end_point = config["end_point"]
        self.__event_type = config["event_type"]
        self.__ws = dict()
        self.__order_book = dict()
        self.__logger = logging.getLogger(__name__)
        # websocket.enableTrace(True)

    def on_message(self, message):
        try:
            obj = json.loads(message)
            symbol = obj['s'].lower()
            if obj['u'] <= self.__order_book[symbol]['nonce']:
                return
            try:
                self.update_order_book(symbol, obj['b'], "bids")
            except Exception as e:
                self.__logger.warning(e)
                self.__logger.warning(obj)

            try:
                self.update_order_book(symbol, obj['a'], "asks")
            except Exception as e:
                self.__logger.warning(e)
                self.__logger.warning(obj)

            # self.__logger.info(message)
        except Exception as e:
            self.__logger.error(e)

    def update_order_book(self, symbol, new_data, order_book_key):
        order_length = len(self.__order_book[symbol][order_book_key]) - 1
        for order in new_data:

            # find index of price level by binary search, performance can be further improved if do a jump search
            # or exponential search first
            try:
                idx, search_success = util.binary_search(self.__order_book[symbol][order_book_key], 0, order_length, float(order[0]))
            except Exception as e:
                # any unexpected error just skip this record to prevent whole program down
                self.__logger.error(e)
                self.__logger.error(order)
                continue

            # skip if delete price not exist
            if not search_success and float(order[1]) == 0:
                continue
            elif not search_success:
                # if search fail, the final left index of binary search is the right place to insert the price
                # level to keep the list sorted
                new_order = [float(order[0]), float(order[1])]
                self.__order_book[symbol][order_book_key].insert(idx, new_order)
                order_length += 1

            if float(order[1]) > 0:
                self.__order_book[symbol][order_book_key][idx][1] = float(order[1])
            else:
                del self.__order_book[symbol][order_book_key][idx]
                order_length -= 1

    def on_error(self, error):
        self.__logger.error(error)

    def on_close(self):
        self.__logger.info("### closed ###")

    def fetch_order_book(self, symbol, limit=None, params={}):
        ws_symbol = ''.join(symbol.split("/")).lower()
        self.__logger.debug("ws_symbol: " + ws_symbol)
        path = self.__end_point + "/ws/" + ws_symbol + self.__event_type

        # get init order book by REST if not subscribed
        if ws_symbol not in self.__order_book:
            self.__logger.info("Not subsribed. symbol: " + ws_symbol)
            order_book = super().fetch_order_book(symbol, limit=1000)
            self.__order_book[ws_symbol] = order_book

        # create ws and subscribe
        if ws_symbol not in self.__ws:
            self.__logger.info("Web socket not open. Try to connect. symbol: " + ws_symbol)
            ws = websocket.WebSocketApp(path,
                                        on_message=self.on_message,
                                        on_error=self.on_error,
                                        on_close=self.on_close)
            # A thread for every ws
            new_ws = threading.Thread(target=ws.run_forever)
            new_ws.start()
            self.__ws[ws_symbol] = ws

        return self.__order_book[ws_symbol]


class ClientThread(threading.Thread):

    def __init__(self, ws):
        threading.Thread.__init__(self)
        self.__ws = ws
        self.__retry_count = 0
        self.__logger = logging.getLogger(__name__)

    def run(self):
        while True:
            try:
                self.__ws.run_forever()
            except Exception as e:
                self.__logger.error(e)
                self.__logger.error("Retry Count: ")
                self.__logger.error(self.__retry_count)
                self.__retry_count += 1
                time.sleep(3)
                # retry every 3 s if fail
