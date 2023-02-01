import requests
import time

endpoint = "https://api.binance.com/api/v3/depth"
symbols = ['BTCUSDT', 'BTCBUSD']
limit = 1000
imbalance_to_initiate = 0.53
imbalance_to_close_position = 0.65
probability_threshold = -0.2
bid_volume, ask_volume, total_prediction, target_price, stop_price = 0, 0, 0, 0, 0
write_prediction, wrong_prediction, price_before, win_trade_count, open_price = 0, 0, 0, 0, 0
close_position_count, lose_trade_count, pnl = 0, 0, 0
total_prob = - 0.0000000000001
trade_opp_search = True
long_position, short_position, stop_loss_activator = False, False, False
while True:
    while trade_opp_search:
        response_price = requests.get("https://api.binance.com/api/v3/ticker/price", params={'symbol': 'BTCUSDT'})
        current_price = float(response_price.json()['price'])
        # get the volume
        for symbol in symbols:
            response = requests.get(endpoint, params={'symbol': symbol, 'limit': limit})
            data = response.json()
            bid_volume += sum([float(bid[1]) for bid in data['bids']
                               if float(bid[0]) >= (current_price * 0.995)])
            ask_volume += sum([float(ask[1]) for ask in data['asks']
                               if float(ask[0]) <= current_price * 1.005])
        probability_down = bid_volume / (bid_volume + ask_volume)
        probability_up = ask_volume / (bid_volume + ask_volume)

        # check for high probability
        if probability_up > imbalance_to_initiate:
            target_price = current_price * 1.005
            stop_price = current_price * 0.995
            trade_opp_search = False
            long_position = True
        if probability_down > imbalance_to_initiate:
            target_price = current_price * 0.995
            stop_price = current_price * 1.005
            trade_opp_search = False
            short_position = True
        open_price = current_price
        print('up prob:', probability_up, 'down prob', probability_down, current_price)
        time.sleep(5)

    while long_position:
        response_price = requests.get("https://api.binance.com/api/v3/ticker/price", params={'symbol': 'BTCUSDT'})
        current_price = float(response_price.json()['price'])
        print('current_price at a long open:', current_price)
        print('total_prob', total_prob)
        # get the volume
        for symbol in symbols:
            response = requests.get(endpoint, params={'symbol': symbol, 'limit': limit})
            data = response.json()
            bid_volume += sum([float(bid[1]) for bid in data['bids']
                               if float(bid[0]) >= (current_price * 0.99)])
            ask_volume += sum([float(ask[1]) for ask in data['asks']
                               if float(ask[0]) <= current_price * 1.01])
        probability_down = bid_volume / (bid_volume + ask_volume)
        probability_up = ask_volume / (bid_volume + ask_volume)

        # calculate total probability
        if probability_up > probability_down:
            total_prob += (probability_up - 0.5)
        else:
            total_prob -= (probability_down - 0.5)

        # check for stop and target meet
        if current_price > target_price:
            win_trade_count += 1
            print('long position meet target')
            long_position = False
        elif current_price < stop_price:
            lose_trade_count += 1
            print('long stop loss activated')
            long_position = False

        # check total probability to close position
        elif total_prob < probability_threshold:
            stop_loss_activator = True
            print('long position closed < -0.3')
            close_position_count += 1
            pnl += current_price - open_price
            long_position = False
        elif probability_down > imbalance_to_close_position:
            stop_loss_activator = True
            print('long position closed other side prob too high')
            close_position_count += 1
            pnl += current_price - open_price
            long_position = False
        time.sleep(20)

    while short_position:
        response_price = requests.get("https://api.binance.com/api/v3/ticker/price", params={'symbol': 'BTCUSDT'})
        current_price = float(response_price.json()['price'])
        print('current_price at short open:', current_price)
        print('total_prob', total_prob)
        # get the volume
        for symbol in symbols:
            response = requests.get(endpoint, params={'symbol': symbol, 'limit': limit})
            data = response.json()
            bid_volume += sum([float(bid[1]) for bid in data['bids']
                               if float(bid[0]) >= (current_price * 0.995)])
            ask_volume += sum([float(ask[1]) for ask in data['asks']
                               if float(ask[0]) <= current_price * 1.005])
        probability_down = bid_volume / (bid_volume + ask_volume)
        probability_up = ask_volume / (bid_volume + ask_volume)
        # calculate total probability
        if probability_up > probability_down:
            total_prob -= (probability_up - 0.5)
        else:
            total_prob += (probability_down - 0.5)

        # check for stop and target meet
        if current_price < target_price:
            win_trade_count += 1
            print('short position meet target')
            short_position = False
        elif current_price > stop_price:
            lose_trade_count += 1
            print('stop loss activated on short position')
            short_position = False
            # check total probability to close position
        elif total_prob < probability_threshold:
            stop_loss_activator = True
            print('short position closed < -0.3')
            close_position_count += 1
            pnl += current_price - open_price
            long_position = False
        elif probability_up > imbalance_to_close_position:
            stop_loss_activator = True
            print('short closed other side prob too high')
            close_position_count += 1
            pnl += current_price - open_price
            long_position = False
        time.sleep(20)
    trade_opp_search = True
    print('win trades:', win_trade_count, '\n lose trades:', lose_trade_count, '\n closed position:',
          close_position_count, '\n PNL:', pnl)
