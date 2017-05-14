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
        self.buy_pair = 'BTC'
        self.sell_pair = 'ETH'
        self.menu_actions = {
            'main_menu': self.main_menu,
            '1': self.sell_order_form,
            '2': self.buy_order_form,
            '3': self.get_order_book,
            '4': self.get_user_orders,
            '5': self.main_balances,
            '6': self.main_cancel,
            '7': self.set_buy_pair,
            '8': self.set_sell_pair,
            '9': self.back,
            '0': self.exit,
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
        self.menu_balances = {
            'main_balances': self.main_balances,
            '1' : self.market_balances,
            '2' : self.account_balances,
            '9' : self.back,
            '0' : self.exit
        }
        self.buy_pairs = ['BTC', 'ETH', 'XMR', 'USDT']
        self.sell_pairs = ['AMP', 'ARDR', 'BCN', 'BCY', 'BELA', 'BLK', 'BTCD', 'BTM', 'BTS', 'BURST', 'CLAM', 'DASH', 'DCR', \
                           'DGB', 'DOGE', 'EMC2', 'ETC', 'ETH', 'EXP', 'FCT', 'FLDC', 'FLO', 'GAME', 'GNO', 'GNT', 'GRC', \
                           'HUC', 'LBC', 'LSK', 'LTC', 'MAID', 'NAUT', 'NAV', 'NEOS', 'NMC', 'NOTE', 'NXC', 'OMNI', 'PASC', \
                           'PINK', 'POT', 'PPC', 'RADS', 'REP', 'RIC', 'SBD', 'SC', 'SJCX', 'STEEM', 'STR', 'STRAT', 'SYS', \
                           'VIA', 'VRC', 'VTC', 'XBC', 'XCP', 'XEM', 'XMR', 'XRP', 'XVC' 'ZEC']
        self.stop_signal = False

    def main(self):
        self.startup_check()
        self.main_menu()


    def startup_check(self):
        if self.buy_pair not in self.buy_pairs:
            self.set_buy_pair()

        elif self.sell_pair not in self.sell_pairs:
            self.set_sell_pair()

        else:
            self.set_currency_pair()

        return

    # Main menu
    def main_menu(self):
        while self.stop_signal == False:
            print "Choose an action :\n1. Sell, 2. Buy, 3. Get Order Book, 4. Get Orders, 5. Get Balances, 6. Cancel order menu 7. Set buy Pair, 8. Set sell pair , 0. Exit"
            choice = raw_input(" >>  ")
            self.exec_menu(choice)
         
        return

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
        return

    def sell_order_form(self):
        self.sell_order_sentence()
        amount = self.choose_amount()
        price = self.choose_price()
        rsp = api.set_sell_order(self.currency_pair, price, amount)

        return

    def buy_order_form(self):
        self.buy_order_sentence()
        amount = self.choose_amount()
        price = self.choose_price()
        rsp = api.set_buy_order(self.currency_pair, price, amount)

        return

    def choose_amount(self):
        try:
            print "Set an amount of ", self.sell_pair, " :"
            choice = float(raw_input(" >>  "))
            return choice
        except ValueError:
            print("That's not a float!")

    def choose_price(self):
        try:
            print "Set the price in ", self.buy_pair, " :"
            choice = float(raw_input(" >>  "))
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

        if self.sell_pair == None:
            self.set_sell_pair()

        return


    def set_sell_pair(self):
        print "Choose the buy pair (", self.sell_pairs, ")"
        choice = raw_input(" >>  ")
        choice = choice.upper()
        
        if choice in self.sell_pairs:
            self.sell_pair = choice
        else:
            self.set_sell_pair()
        self.set_currency_pair()
        return

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
        self.sys.exit()
        self.stop_signal = True

    def sell_order_sentence(self):
        print "------------------------------------------------------------------------------------------------------------------------"
        print "                                                 SELL ORDERS                                                            "
        print "------------------------------------------------------------------------------------------------------------------------"

    def buy_order_sentence(self):
        print "------------------------------------------------------------------------------------------------------------------------"
        print "                                                 BUY ORDERS                                                             "
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