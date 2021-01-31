### Description
This is a simple order book managing program by overriding the `fetch_order_book` function
of `ccxt.binance`.
It will get init order book by REST implemented by ccxt and keep updating it by
using a websocket connecting to binance.

### Usage
```
custom_binance = CustomBinance()
order_book = custom_binance.fetch_order_book(symbol)
```
By calling the function, a cached order book (which is updating in realtime) will be return.

### Scalability
1. To allow multiple application accessing the latest order book. An instance can be created in cloud (e.g. set up a
AWS EC2 instance and keep the script running). Other applications can connect to this program to retrieve the latest data.
Kafka or other message queue can be used as the connection between different applications. For example, this program can
publish the latest order book of different symbol in different topics to act as a producer. Other applications can get the
message as a consumer.
2. To ensure the high availability, this program can be run on a cluster. For example, we can build a hadoop cluster.
Running high availability flink and kafka on it. Run the program base on this infrastructure as a flink job. 
Zookeeper will check the heartbeat of each instance. Once the program or any infrastructure failed or the instance is down, 
the program will be restarted automatically on different instance.
3. To further enhance the performance of this program, exponential search or jump search can be preformed before binary
serach. This can reduce the searching time.