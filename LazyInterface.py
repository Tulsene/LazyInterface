#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Command Line interface to interact with poloniex
# if you don't get it, don't use it

import sys, os
import logging
import apiInterface
from decimal import *

class LazyInterface:
    getcontext().prec = 8

    def __init__(self):
        self.currency_pair = None
        self.buy_pair = 'ETH'
        self.sell_pair = 'REP'
        self.menu_actions = {
            'main_menu': self.main_menu,
            '1': self.main_sell,
            '2': self.main_buy,
            '3': self.get_order_book,
            '4': self.get_user_orders,
            '5': self.main_balances,
            '6': self.main_cancel,
            '7': self.set_buy_pair,
            '8': self.set_sell_pair,
            '9': self.back,
            '0': self.exit,
        }
        self.menu_sell = {
            'main_sell': self.main_sell,
            '1': self.sell_order_form,
            '2': self.margin_sell_order_form,
            '9': self.back,
            '0': self.exit,
        }
        self.menu_buy = {
            'main_buy': self.main_buy,
            '1': self.buy_order_form,
            '2': self.margin_buy_order_form,
            '9': self.back,
            '0': self.exit,
        }
        self.menu_balances = {
            'main_balances': self.main_balances,
            '1' : self.market_balances,
            '2' : self.account_balances,
            '9' : self.back,
            '0' : self.exit,
        }
        self.menu_cancel = {
            'main_cancel': self.main_cancel,
            '1': self.cancel_all,
            '2': self.cancel_buys,
            '3': self.cancel_sells,
            '4': self.cancel_specific_order,
            '9': self.back,
            'O': self.exit,
        }
        
        self.buy_pairs = ['BTC', 'ETH', 'XMR', 'USDT']
        self.btc_sell_pairs = ['AMP', 'ARDR', 'BCN', 'BCY', 'BELA', 'BLK', 'BTCD', 'BTM', 'BTS', 'BURST', 'CLAM', 'DASH', 'DCR', \
                           'DGB', 'DOGE', 'EMC2', 'ETC', 'ETH', 'EXP', 'FCT', 'FLDC', 'FLO', 'GAME', 'GNO', 'GNT', 'GRC', \
                           'HUC', 'LBC', 'LSK', 'LTC', 'MAID', 'NAUT', 'NAV', 'NEOS', 'NMC', 'NOTE', 'NXC', 'OMNI', 'PASC', \
                           'PINK', 'POT', 'PPC', 'RADS', 'REP', 'RIC', 'SBD', 'SC', 'SJCX', 'STEEM', 'STR', 'STRAT', 'SYS', \
                           'VIA', 'VRC', 'VTC', 'XBC', 'XCP', 'XEM', 'XMR', 'XRP', 'XVC' 'ZEC']
        self.eth_sell_pairs = ['GNT', 'ETC', 'GNO', 'STEEM', 'ZEC', 'LSK', 'REP']
        self.xmr_sell_pairs = ['LTC', 'ZEC', 'NXT', 'DASH', 'MAID', 'BLK', 'BTCD', 'BCN']
        self.usdt_sell_pairs = ['BTC', 'XRP', 'STR', 'LTC', 'ETH', 'ETC', 'NXT', 'ZEC', 'DASH', 'XMR', 'REP']
        self.margin_sell_pairs = ['BTS', 'CLAM', 'DASH', 'DOGE', 'ETH', 'FCT', 'LTC', 'MAID', 'STR', 'XMR', 'XRP']
        self.stop_signal = False

    def main(self):
        self.startup_check()
        self.main_menu()


    def startup_check(self):
        if self.buy_pair not in self.buy_pairs:
            self.set_buy_pair()

        self.check_sell_pair()

        if self.currency_pair == None:
            self.set_currency_pair()

    # Main menu
    def main_menu(self):
        while self.stop_signal == False:
            print "Choose an action :\n1. Sell, 2. Buy, 3. Get Order Book, 4. Get Orders, 5. Get Balances, 6. Cancel order menu 7. Set buy Pair, 8. Set sell pair , 0. Exit"
            choice = raw_input(" >>  ")
            self.exec_menu(choice)

    # Execute menu
    def exec_menu(self, choice):
        ch = choice.lower()
        if ch == '':
            self.menu_actions['main_menu']()
        else:
            try:
                self.menu_actions[ch]()
            except KeyError:
                print "Invalid selection, please try again.\n"
                self.menu_actions['main_menu']()

    def main_sell(self):
        print "Kind of sell order : 1. Normal, 2. Margin, 9. Back to main menu , 0. Exit"
        choice = raw_input(" >>  ")
        ch = choice.lower()

        if ch == '':
            self.menu_sell['main_sell']()
        else:
            try:
                self.menu_sell[ch]()
            except KeyError:
                print "Invalid selection, please try again.\n"
                self.menu_sell['main_sell']()

    def sell_order_form(self):
        self.sell_order_sentence()
        amount = self.choose_amount()
        price = self.choose_price()
        rsp = api.set_sell_order(self.currency_pair, price, amount)

    def margin_sell_order_form(self):
        if self.buy_pair != 'BTC':
            self.buy_pair = 'BTC'

        if self.sell_pair not in self.margin_sell_pairs:
            self.set_margin_sell_pair()

        self.margin_sell_order_sentence()
        amount = self.choose_amount()
        price = self.choose_price()
        rsp = api.set_margin_sell_order(self.currency_pair, price, amount)

    def main_buy(self):
        print "Kind of buy order : 1. Normal, 2. Margin, 9. Back to main menu , 0. Exit"
        choice = raw_input(" >>  ")
        ch = choice.lower()

        if ch == '':
            self.menu_buy['main_buy']()
        else:
            try:
                self.menu_buy[ch]()
            except KeyError:
                print "Invalid selection, please try again.\n"
                self.menu_buy['main_buy']()

    def buy_order_form(self):
        self.buy_order_sentence()
        amount = self.choose_amount()
        price = self.choose_price()
        rsp = api.set_buy_order(self.currency_pair, price, amount)
        self.action_end_sentence()

    def margin_buy_order_form(self):
        if self.buy_pair != 'BTC':
            self.buy_pair = 'BTC'

        if self.sell_pair not in self.margin_sell_pairs:
            self.set_margin_sell_pair()

        self.margin_buy_order_sentence()
        amount = self.choose_amount()
        price = self.choose_price()
        rsp = api.set_margin_buy_order(self.currency_pair, price, amount)
        self.action_end_sentence()

    def choose_amount(self):
        try:
            print "Set an amount of ", self.sell_pair, " :"
            choice = float(raw_input(" >>  "))
            print choice
            return choice
        except ValueError:
            print("That's not a float!")

    def choose_price(self):
        try:
            print "Set the price in ", self.buy_pair, " :"
            choice = float(raw_input(" >>  "))
            print choice
            return choice
        except ValueError:
            print("That's not a float!")

    def get_order_book(self):
        sell_orders, buy_orders = api.get_order_book(self.currency_pair)
        self.asks_bids_sentence()
        i = 0

        for order in sell_orders:
            print order, "        ", buy_orders[i]
            i += 1
        
        self.action_end_sentence()

    def get_user_orders(self):
        new_buy_orders, new_sell_orders = api.get_orders(self.currency_pair)
        self.sell_order_sentence()
        
        if new_sell_orders:
            for order in new_sell_orders:
                print order
            self.action_end_sentence()

        else:
            print "Empty"
            self.action_end_sentence()

        self.buy_order_sentence()
        
        if new_buy_orders:
            for order in new_buy_orders:
                print order
            self.action_end_sentence()

        else:
            print "Empty"
            self.action_end_sentence()

    def main_balances(self):
        print "What kind of balances do you want?\n 1. Buy & Sell pair balances, 2. Whole account balance, 9. Back, 9. Exit"
        choice = raw_input(" >>  ")

        ch = choice.lower()
        if ch == '':
            self.menu_balances['main_balances']()
        else:
            try:
                self.menu_balances[ch]()
            except KeyError:
                print "Invalid selection, please try again.\n"
                self.menu_balances['main_balances']()

    def market_balances(self):
        buy_balance, sell_balance = api.get_balance(self.buy_pair, self.sell_pair)
        self.market_balances_sentence()
        
        print " - ", buy_balance, self.buy_pair, "\n - ", sell_balance, self.sell_pair
        self.action_end_sentence()

    def account_balances(self):
        balances = api.get_balances()
        self.account_balances_sentence()

        for balance in balances:
            print " - ", balance[1], balance[0]

        self.action_end_sentence()

    def main_cancel(self):
        print "what kind of cancel ?\n 1. cancel all, 2. cancel buys, 3. cancel sells, 4. cancel specific order, 9. Back to main menu, 0. Exit"
        choice = raw_input(" >>  ")

        ch = choice.lower()
        if ch == '':
            self.menu_cancel['main_cancel']()
        else:
            try:
                self.menu_cancel[ch]()
            except KeyError:
                print "Invalid selection, please try again.\n"
                self.menu_cancel['main_cancel']()

    def cancel_all(self):
        self.cancel_all_orders_sentence()
        api.cancel_all(self.currency_pair)
        self.action_end_sentence()

    def cancel_buys(self):
        buy_orders, sell_orders = api.get_orders(self.currency_pair)
        self.cancel_buy_orders_sentence()

        for order in buy_orders:
            api.cancel_order(self.currency_pair, order[0])

        self.action_end_sentence()

    def cancel_sells(self):
        buy_orders, sell_orders = api.get_orders(self.currency_pair)
        self.cancel_sell_orders_sentence()

        for order in sell_orders:
            api.cancel_order(self.currency_pair, order[0])

        self.action_end_sentence()

    def cancel_specific_order(self):
        order_to_delete = 0
        self.get_user_orders()
        buy_orders, sell_orders = api.get_orders(self.currency_pair)
        print "Wich order do you want to cancel ? :"
        choice = raw_input(" >>  ")
        choice = int(choice)

        for order in buy_orders:
            if choice == order[0]:
                order_to_delete = choice
        
        for order in buy_orders:
            if choice == order[0]:
                order_to_delete = choice

        if order_to_delete != 0:
            self.cancel_order_sentence()
            api.cancel_order(self.currency_pair, choice)
            self.action_end_sentence()
            
        else:
            print "The order don't exist!"
            self.main_cancel()


    def set_buy_pair(self):
        print "Choose the buy pair (", self.buy_pairs, ")"
        choice = raw_input(" >>  ")
        choice = choice.upper()

        if choice in self.buy_pairs:
            self.buy_pair = choice
        else:
            self.set_buy_pair()

        self.check_sell_pair()
        self.action_end_sentence()

    def set_sell_pair(self):
        self.sell_pair = 0
        self.check_sell_pair()

    def check_sell_pair(self):
        if self.buy_pair == 'BTC':
            if self.sell_pair not in self.btc_sell_pairs:
                self.set_btc_sell_pair()

        if self.buy_pair == 'ETH':
            if self.sell_pair not in self.eth_sell_pairs:
                self.set_eth_sell_pair()

        if self.buy_pair == 'XMR':
            if self.sell_pair not in self.xmr_sell_pairs:
                self.set_xmr_sell_pair()

        if self.buy_pair == 'USDT':
            if self.sell_pair not in self.usdt_sell_pairs:
                self.set_usdt_sell_pair()


    def set_btc_sell_pair(self):
        print "Choose the sell pair (", self.btc_sell_pairs, ")"
        choice = raw_input(" >>  ")
        choice = choice.upper()
        
        if choice in self.btc_sell_pairs:
            self.sell_pair = choice
        else:
            self.set_btc_sell_pair()

        self.set_currency_pair()
        self.action_end_sentence()

    def set_eth_sell_pair(self):
        print "Choose the sell pair (", self.eth_sell_pairs, ")"
        choice = raw_input(" >>  ")
        choice = choice.upper()
        
        if choice in self.eth_sell_pairs:
            self.sell_pair = choice
        else:
            self.set_eth_sell_pair()

        self.set_currency_pair()
        self.action_end_sentence()

    def set_xmr_sell_pair(self):
        print "Choose the sell pair (", self.xmr_sell_pairs, ")"
        choice = raw_input(" >>  ")
        choice = choice.upper()
        
        if choice in self.xmr_sell_pairs:
            self.sell_pair = choice
        else:
            self.set_xmr_sell_pair()

        self.set_currency_pair()
        self.action_end_sentence()

    def set_usdt_sell_pair(self):
        print "Choose the sell pair (", self.usdt_sell_pairs, ")"
        choice = raw_input(" >>  ")
        choice = choice.upper()
        
        if choice in self.usdt_sell_pairs:
            self.sell_pair = choice
        else:
            self.set_usdt_sell_pair()

        self.set_currency_pair()
        self.action_end_sentence()

    def set_margin_sell_pair(self):
        print "Choose the margin sell pair (", self.margin_sell_pairs, ")"
        choice = raw_input(" >>  ")
        choice = choice.upper()
        
        if choice in self.margin_sell_pairs:
            self.sell_pair = choice
        else:
            self.set_margin_sell_pair()

        self.set_currency_pair()
        self.action_end_sentence()

    def set_currency_pair(self):
        self.currency_pair = self.buy_pair, "_", self.sell_pair
        self.currency_pair = str(self.currency_pair)

        for ch in ["'", ",", " ", "(", ")"]:
            if ch in self.currency_pair:
                self.currency_pair = self.currency_pair.replace(ch, "")

    # Back to main menu
    def back(self):
        self.menu_actions['main_menu']()
     
    # Exit program
    def exit(self):
        self.stop_signal = True
        sys.exit(0)

    def sell_order_sentence(self):
        print "------------------------------------------------------------------------------------------------------------------------"
        print "                                                 SELL ORDERS                                                            "
        print "------------------------------------------------------------------------------------------------------------------------"

    def buy_order_sentence(self):
        print "------------------------------------------------------------------------------------------------------------------------"
        print "                                                 BUY ORDERS                                                             "
        print "------------------------------------------------------------------------------------------------------------------------"

    def margin_sell_order_sentence(self):
        print "------------------------------------------------------------------------------------------------------------------------"
        print "                                             MARGIN SELL ORDERS                                                         "
        print "------------------------------------------------------------------------------------------------------------------------"

    def margin_buy_order_sentence(self):
        print "------------------------------------------------------------------------------------------------------------------------"
        print "                                              MARGIN BUY ORDERS                                                             "
        print "------------------------------------------------------------------------------------------------------------------------"

    def asks_bids_sentence(self):
        print "------------------------------------------------------------------------------------------------------------------------"
        print "                      ASKS                                                             BIDS                             "
        print "------------------------------------------------------------------------------------------------------------------------"
    
    def market_balances_sentence(self):
        print "------------------------------------------------------------------------------------------------------------------------"
        print "                                               MARKET BALANCES                                                          "
        print "------------------------------------------------------------------------------------------------------------------------"
    
    def account_balances_sentence(self):
        print "------------------------------------------------------------------------------------------------------------------------"
        print "                                               ACCOUNT BALANCES                                                         "
        print "------------------------------------------------------------------------------------------------------------------------"
    
    def cancel_all_orders_sentence(self):
        print "------------------------------------------------------------------------------------------------------------------------"
        print "                                              CANCEL ALL ORDERS                                                         "
        print "------------------------------------------------------------------------------------------------------------------------"
    
    def cancel_buy_orders_sentence(self):
        print "------------------------------------------------------------------------------------------------------------------------"
        print "                                              CANCEL BUY ORDERS                                                         "
        print "------------------------------------------------------------------------------------------------------------------------"
    
    def cancel_sell_orders_sentence(self):
        print "------------------------------------------------------------------------------------------------------------------------"
        print "                                              CANCEL SELL ORDERS                                                        "
        print "------------------------------------------------------------------------------------------------------------------------"
    
    def cancel_order_sentence(self):
        print "------------------------------------------------------------------------------------------------------------------------"
        print "                                              ORDER CANCELLED                                                           "
        print "------------------------------------------------------------------------------------------------------------------------"

    def action_end_sentence(self):
        print "------------------------------------------------------------------------------------------------------------------------"

     
api = apiInterface.ApiInterface()
lazyInterface = LazyInterface()

# Main Program
if __name__ == "__main__":
    # Launch main_menu
    lazyInterface.main()