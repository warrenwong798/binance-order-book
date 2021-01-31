import time
import logging

from CustomBinance import CustomBinance

end_point = "wss://stream.binance.com:9443"
event_type = "@depth"
symbol = ["BTC/USDT"]
# init a CustomBinance instance
custom_binance = CustomBinance(config={"end_point": end_point, "event_type": event_type})


# get the latest order book
def get_order_book(symbol):
    order_book = custom_binance.fetch_order_book(symbol)
    return order_book


# keep printing the latest order book every 5s
def handle_order_book(symbol):
    while True:
        order_book = get_order_book(symbol)
        logging.info("order book:")
        logging.info(order_book)
        time.sleep(5)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s:%(message)s')
    for s in symbol:
        handle_order_book(s)
