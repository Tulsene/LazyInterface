#!/usr/bin/env python
# -*- coding: utf-8 -*-
# market making script for lazy whale  market maker
# if you don't get it, don't use it

import logging
import time
import urllib2
import poloniex
import os
import sys
from decimal import *

if not "API_KEY" in os.environ or not "API_SECRET" in os.environ:
    print "Please set the environment variables api_secret and api_key"
    sys.exit(1)
else:
    api_key = os.environ["API_KEY"]
    api_secret = os.environ["API_SECRET"]

poloniex = poloniex.Poloniex(api_key, api_secret)


class ApiInterface:
    getcontext().prec = 8  # Set the precision for decimal

    def api_sleep(self):
        """Sleeping function, call it to make a break in the code execution.
        """
        time.sleep(7)

    def get_balance(self, buy_pair, sell_pair):
        """Get the user balance.

        Get the buy pair balance.
        Get the sell pair balance.
        Return the balance of the buy and sell pair.
        """
        try:
            balances = poloniex.returnBalances()
            buy_balance = balances[buy_pair]
            sell_balance = balances[sell_pair]

            log = 'buy_balance : ', buy_balance, 'sell_balance : ', sell_balance
            logging.info(log)  # Logs a message with level INFO on the root logger.

            return buy_balance, sell_balance

        except (urllib2.HTTPError, urllib2.URLError) as e:
            logging.error(e.code)  # Logs a message with level ERROR on the root logger

            self.api_sleep()
            self.get_balance()

    def get_balances(self):
        """Get the user balances.

        Get all balances.
        Init the list of non empty balances.
        Format the amount.
        Select non empty amount.
        Format ticker name.
        Add balance to non empty balances
        Return balances.
        """
        try:
            balances = poloniex.returnBalances()
            balances = balances.items()
            balances_fetched = []

            for balance in balances:
                balance = list(balance)
                balance[1] = str(balance[1])

                if balance[1] != '0.00000000':
                    balance[0] = str(balance[0])
                    balances_fetched.append(balance)
            
            return balances_fetched

        except (urllib2.HTTPError, urllib2.URLError) as e:
            logging.error(e.code)  # Logs a message with level ERROR on the root logger

            self.api_sleep()
            self.get_balances()

    def get_orders(self, currency_pair):
        """Get the user actives orders.

        Get orders from the marketplace.
        Call the function fetch_orders to organize the user buy and sell order book.
        Return new_buy_orders and new_sell_orders.
        """
        try:
            orders = poloniex.returnOpenOrders(currency_pair)

            log = 'orders : ', str(orders)
            logging.info(log)

            new_buy_orders, new_sell_orders = self.fetch_orders(orders)

        except (urllib2.HTTPError, urllib2.URLError) as e:
            logging.error(e.code)

            self.api_sleep()
            new_buy_orders, new_sell_orders = self.get_orders(currency_pair)

        return new_buy_orders, new_sell_orders

    def fetch_orders(self, orders):
        """Fetch buy and sell orders from self.orders.

        Fetch new_buy_orders, new_sell_orders from orders.
        Return new_buy_orders, new_sell_orders both ordered with the smallest rate @0
        """
        new_buy_orders, new_sell_orders = [], []

        for item in orders:
            order_number = int(item['orderNumber'])
            order_type = str(item['type'])
            order_rate = Decimal(item['rate'])
            order_amount = Decimal(item['amount'])

            if order_type == 'buy':
                new_buy_orders.append([order_number, order_amount, order_rate])

            if order_type == 'sell':
                new_sell_orders.append([order_number, order_amount, order_rate])

        return new_buy_orders, new_sell_orders

    def set_sell_order(self, currency_pair, rate, amount):
        """Set sell order.

        Catch result, fetch it.
        Return result.
        """
        try:
            result = poloniex.sell(currency_pair, rate, amount)

            log = 'set_sell_order(', currency_pair, ', ', rate, ', ', amount, ') : ', result
            logging.warning(log)

            result = int(result['orderNumber'])
            result = [result, amount, rate]

            return result

        except (urllib2.HTTPError, urllib2.URLError) as e:
            logging.error(e.code)

            return self.retry_set_sell_order(currency_pair, rate, amount)

    def set_margin_sell_order(self, currency_pair, rate, amount):
        """Set margin sell order.

        Catch result, fetch it.
        Return result.
        """
        try:
            result = poloniex.marginSell(currency_pair, rate, amount)

            log = 'set_margin_sell_order(', currency_pair, ', ', rate, ', ', amount, ') : ', result
            logging.warning(log)

            result = int(result['orderNumber'])
            result = [result, amount, rate]

            return result

        except (urllib2.HTTPError, urllib2.URLError) as e:
            logging.error(e.code)

            return self.retry_set_margin_sell_order(currency_pair, rate, amount)

    def retry_set_sell_order(self, currency_pair, rate, amount):
        """Retry to set a sell order.

        Assign new_sell_orders by calling get_orders(currency_pair).
        Search for the same rate in new_buy_orders and return corresponding item.
        Otherwise return set_sell_order().
        """
        self.api_sleep()

        # Putting 'result' in string since the variable is not locally defined in the function
        log = 'retry_set_sell_order(', currency_pair, ', ', rate, ', ', amount, ') : result'
        logging.warning(log)

        new_buy_orders, new_sell_orders = self.get_orders(currency_pair)

        for item in new_sell_orders:
            if rate in item:
                logging.warning('sell order already active')
                return item

        return self.set_sell_order(currency_pair, rate, amount)

    def retry_set_margin_sell_order(self, currency_pair, rate, amount):
        """Retry to set a margin sell order.

        Assign new_sell_orders by calling get_orders(currency_pair).
        Search for the same rate in new_buy_orders and return corresponding item.
        Otherwise return set_margin_sell_order().
        """
        self.api_sleep()

        # Putting 'result' in string since the variable is not locally defined in the function
        log = 'retry_set_margin_sell_order(', currency_pair, ', ', rate, ', ', amount, ') : result'
        logging.warning(log)

        new_buy_orders, new_sell_orders = self.get_orders(currency_pair)

        for item in new_sell_orders:
            if rate in item:
                logging.warning('margin sell order already active')
                return item

        return self.set_margin_sell_order(currency_pair, rate, amount)

    def set_several_sell_orders(self, currency_pair, price_start, amount, nb_orders, increment):
        """Call as much as set_sell_order() is needed.
        Call nb_orders times set_sell_order() and add the response to sell_orders
        Return sell_orders ordered with the smallest rate @0
        """
        sell_orders = []

        log = 'set_several_sell_orders(', nb_orders, ')'
        logging.warning(log)

        while nb_orders > 0:
            order = self.set_sell_order(currency_pair, price_start, amount)
            sell_orders.append(order)
            price_start += increment
            nb_orders -= 1

        return sell_orders

    def set_several_margin_sell_orders(self, currency_pair, price_start, amount, nb_orders, increment):
        """Call as much as set_sell_order() is needed.

		Call nb_orders times set_sell_order() and add the response to sell_orders
        Return sell_orders ordered with the smallest rate @0
        """
        sell_orders = []

        log = 'set_several_margin_sell_orders(', nb_orders, ')'
        logging.warning(log)

        while nb_orders > 0:
            order = self.set_margin_sell_order(currency_pair, price_start, amount)
            sell_orders.append(order)
            price_start += increment
            nb_orders -= 1

        return sell_orders

    def set_buy_order(self, currency_pair, rate, amount):
        """Set buy order.

        Catch result, fetch it.
        Return result.
        """
        try:
            result = poloniex.buy(currency_pair, rate, amount)

            log = 'set_buy_order(', currency_pair, ', ', rate, ', ', amount, ') : ', result
            logging.warning(log)

            result = int(result['orderNumber'])
            result = [result, amount, rate]

            return result

        except (urllib2.HTTPError, urllib2.URLError) as e:
            logging.error(e.code)

            return self.retry_set_buy_order(currency_pair, rate, amount)

    def set_margin_buy_order(self, currency_pair, rate, amount):
        """Set margin buy order.

        Catch result, fetch it.
        Return result.
        """
        try:
            result = poloniex.marginBuy(currency_pair, rate, amount)

            log = 'set_margin_buy_order(', currency_pair, ', ', rate, ', ', amount, ') : ', result
            logging.warning(log)

            result = int(result['orderNumber'])
            result = [result, amount, rate]

            return result

        except (urllib2.HTTPError, urllib2.URLError) as e:
            logging.error(e.code)

            return self.retry_set_margin_buy_order(currency_pair, rate, amount)

    def retry_set_buy_order(self, currency_pair, rate, amount):
        """Retry to set a buy order.

        Assign new_buy_orders by calling get_orders(currency_pair).
        Search for the same rate in new_buy_orders and return corresponding item.
        Otherwise return set_buy_order().
        """
        self.api_sleep()

        # Putting 'result' in string since the variable is not locally defined in the function
        log = 'retry_set_buy_order(', currency_pair, ', ', rate, ', ', amount, ') : result'
        logging.warning(log)

        new_buy_orders, new_sell_orders = self.get_orders(currency_pair)

        for item in new_buy_orders:
            if rate in item:
                logging.warning('buy order already active')
                return item

        return self.set_buy_order(currency_pair, rate, amount)

    def retry_set_margin_buy_order(self, currency_pair, rate, amount):
        """Retry to set a margin buy order.

        Assign new_buy_orders by calling get_orders(currency_pair).
        Search for the same rate in new_buy_orders and return correspondign item.
        Otherwise return set_margin_buy_order().
        """
        self.api_sleep()

        # Putting 'result' in string since the variable is not locally defined in the function
        log = 'retry_set_margin_buy_order(', currency_pair, ', ', rate, ', ', amount, ') : result'
        logging.warning(log)

        new_buy_orders, new_sell_orders = self.get_orders(currency_pair)

        for item in new_buy_orders:
            if rate in item:
                logging.warning('margin buy order already active')
                return item

        return self.set_margin_buy_order(currency_pair, rate, amount)

    def set_several_buy_orders(self, currency_pair, price_start, amount, nb_orders, increment):
        """Call i times set_buy_order().

        Call nb_orders times set_buy_order() and add the response to sell_orders
        Return buy_orders ordered with the smallest rate @0
        """
        buy_orders = []

        log = 'set_several_buy_orders(', nb_orders, ')'
        logging.warning(log)

        while nb_orders > 0:
            order = self.set_buy_order(currency_pair, price_start, amount)
            buy_orders.insert(0, order)
            price_start -= increment
            nb_orders -= 1

        return buy_orders

    def set_several_margin_buy_orders(self, currency_pair, price_start, amount, nb_orders, increment):
        """Call i times set_buy_order().

        Call nb_orders times set_buy_order() and add the response to sell_orders
        Return buy_orders ordered with the smallest rate @0
        """
        buy_orders = []

        log = 'set_several_margin_buy_orders(', nb_orders, ')'
        logging.warning(log)

        while nb_orders > 0:
            order = self.set_margin_buy_order(currency_pair, price_start, amount)
            buy_orders.insert(0, order)
            price_start -= increment
            nb_orders -= 1

        return buy_orders

    def cancel_order(self, currency_pair, order_number):
        """Cancel order_number order.

        Return response from poloniex.cancel()
        """
        try:
            result = poloniex.cancel(currency_pair, order_number)

            log = 'cancel_order(', currency_pair, ', ', order_number, '), result : ', result
            logging.warning(log)

            return result

        except (urllib2.HTTPError, urllib2.URLError) as e:
            logging.error(e.code)

            return self.retry_cancel_order(currency_pair, order_number)

    def retry_cancel_order(self, currency_pair, order_number):
        self.api_sleep()
        orders = poloniex.returnOpenOrders(currency_pair)

        str_order_number = str(order_number)

        for order in orders:
            if order['orderNumber'] == str_order_number:
                return self.cancel_order(currency_pair, order_number)

        rsp = 'Already canceled'

        return rsp

    def cancel_all(self, currency_pair):
        """Cancel all actives orders."""
        new_buy_orders, new_sell_orders = self.get_orders(currency_pair)

        logging.warning('cancel_all()')

        for item in new_buy_orders:
            self.cancel_order(currency_pair, item[0])

        for item in new_sell_orders:
            self.cancel_order(currency_pair, item[0])

    def get_order_book(self, currency_pair):
        """Get the order book from the marketplace."""
        try :
            orders = poloniex.returnOrderBook(currency_pair)
            sell_orders, buy_orders = self.fetch_order_book(orders)
        except (urllib2.HTTPError, urllib2.URLError) as e:
            logging.error(e.code)
            self.api_sleep()
            self.get_order_book(currency_pair)

        return sell_orders, buy_orders

    def fetch_order_book(self, orders):
        """Fetch order book.

        Init sell_orders_fetched with filing data for Asks book.
        Format data from fetch_order_book.
        Calculate bitcoin value of an order.
        Sum of all orders.
        Add order to sell_orders_fetched.
        Remove filing data.
        Do the same for Bids.
        Return sell_orders & buy_orders."""
        sell_orders = orders['asks']
        sell_orders_fetched = []
        test = [0, 0, 0, 0]
        sell_orders_fetched.append(test)

        for order in sell_orders:
            order[0] = float(order[0])
            order.append("{0:.8}".format(order[0] * order[1]))
            order.append("{0:.8}".format(float(order[2]) + float(sell_orders_fetched[-1][3])))
            sell_order_fetched = list(order)
            sell_orders_fetched.append(sell_order_fetched)

        sell_orders_fetched.remove(sell_orders_fetched[0])

        buy_orders = orders['bids']
        buy_orders_fetched = []
        buy_orders_fetched.append(test)

        for order in buy_orders:
            order[0] = float(order[0])
            order.append("{0:.8}".format(order[0] * order[1]))
            order.append("{0:.8}".format(float(order[2]) + float(buy_orders_fetched[-1][3])))
            buy_order_fetched = list(order)
            buy_orders_fetched.append(buy_order_fetched)

        buy_orders_fetched.remove(buy_orders_fetched[0])
        
        return sell_orders_fetched, buy_orders_fetched



