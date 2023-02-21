from time import sleep
from order_book import get_probabilities
loop_counter = 0
SYMBOLS = ['BTCUSDT', 'BTCBUSD']

# trading opportunity
while True:
    loop_counter += 1
    print(loop_counter)
    # region 1.1 Get the prediction

    # endregion

    # region 1.2 add new value to dataset
    # endregion

    # region 2. Get Adam Watcher value
    # endregion 2. Get Adam Watcher value

    # region 2.1 get order book
    # get probability of price go up and down
    probability_down, probability_up = get_probabilities(SYMBOLS, bid_multiplier=0.995, ask_multiplier=1.005)
    print('prob down and up', probability_down, probability_up)

    # endregion

    # region 2.2. Richest address on blockchain
    # endregion

    # region 2.3 google search
    # endregion

    # region 2.4 interest rate

    # endregion

    # region 2.5 news website
    # endregion

    # region 2.6 Reddit
    # endregion

    # region  2.7 CPI PPI

    # end region

    # region 2.8 Twitter
    # endregion

    # region 2.9 Youtube
    # endregion

    # region 3.Make decision about the trade
    # endregion

    sleep(30)

# region when a trade is open
# endregion
