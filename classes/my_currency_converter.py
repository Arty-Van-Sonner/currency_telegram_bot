import requests
from bs4 import BeautifulSoup as bs
from dateutil.parser import parse
from pprint import pprint
import re
import yahoo_fin.stock_info as si
from datetime import datetime, timedelta
from cbrf.models import DailyCurrenciesRates
import json
from currency_converter import CurrencyConverter as cc

from thread import Thread

import global_variables as gv    

class MyCurrencyConverter:
    '''
    
    '''
    from currency import Currency
    __source_currency: Currency
    __receiver_currency: Currency
    __source_amount: float
    __right_arrow = None
    __left_arrow = None
    __left_bracket = None
    __right_bracket = None

    def __init__(self, string_from_bot: str, data_on_the_task_condition = None) -> None:
        if data_on_the_task_condition is None:
            self.__source_currency = None
            self.__receiver_currency = None
            self.__source_amount = None
            self.__right_arrow = '->'
            self.__left_arrow = '<-'
            self.__left_bracket = '('
            self.__right_bracket = ')'
            self.processing_string(string_from_bot)
        else:
            self.__source_currency = data_on_the_task_condition['base']
            self.__receiver_currency = data_on_the_task_condition['quote']
            self.__source_amount = data_on_the_task_condition['amount']
        self.__source_amount = round(self.__source_amount, 2)
    
    def processing_string(self, string_from_bot: str) -> str:
        count_right_arrow = string_from_bot.count(self.__right_arrow)
        count_left_arrow = string_from_bot.count(self.__left_arrow)
        count_left_bracket = string_from_bot.count(self.__left_bracket)
        count_right_bracket = string_from_bot.count(self.__right_bracket)
        error_strings = []
        if count_right_arrow > 1:
            error_strings.append(f'Error! The right arrows ({self.__right_arrow}) is too much!')
        if count_left_arrow > 1:
            error_strings.append(f'Error! The right arrows ({self.__left_arrow}) is too much!')
        if count_left_bracket > 1:
            error_strings.append(f'Error! The left brackets ({self.__left_bracket}) is too much!')
        if count_right_bracket > 1:
            error_strings.append(f'Error! The right brackets ({self.__right_bracket}) is too much!') 
        if not self.checke_paired_brackets(string_from_bot):
            error_strings.append('Error of paired brackets!')

        if count_right_arrow + count_left_arrow > 1:
            error_strings.append('Error! The arrows are repeated!')

        if len(error_strings) > 0:
            raise gv.ErrorInStringFromUser('\n'.join(error_strings))

        if count_right_arrow + count_left_arrow + count_left_bracket + count_right_bracket == 0:
            list_strings_from_bot = string_from_bot.split()
            self.__source_currency, self.__receiver_currency, self.__source_amount = self.get_parametrs_of_currency_convertion_from_list_strings(list_strings_from_bot) 
        else:
            if count_left_bracket != 1 and count_right_bracket != 1:
                raise gv.ErrorInStringFromUser('Error! The number of parameters in the line does not match the instructions! Brackets error')
            self.__source_currency, self.__receiver_currency, self.__source_amount = self.get_parametrs_of_currency_convertion_by_special_rules(string_from_bot, count_right_arrow, count_left_arrow)

        if self.__source_currency == self.__receiver_currency:
            raise gv.ErrorInStringFromUser('Error! The source currency and the receiver currency are the same!')

    def get_parametrs_of_currency_convertion_from_list_strings(self, list_strings_from_bot: list[str]):
        if len(list_strings_from_bot) != 3:
            raise gv.ErrorInStringFromUser('Error! The number of parameters in the line does not match the instructions!')
        source_currency = gv.сurrencies.get_currency_by_name(list_strings_from_bot[0])
        receiver_currency = gv.сurrencies.get_currency_by_name(list_strings_from_bot[1])
        source_amount = None
        try:
            source_amount = float(list_strings_from_bot[2].replace('  ', '').replace(' ', '').replace(',', '.'))
        except ValueError:
            pass
        error_strings = []
        if source_currency is None:
            error_strings.append(f'Error! The source currency _({list_strings_from_bot[0]})_ has not been determined!')
        if receiver_currency is None:
            error_strings.append(f'Error! The receiver currency _({list_strings_from_bot[1]})_ has not been determined!')
        if source_amount is None:
            error_strings.append(f'Error! The source amount _({list_strings_from_bot[2]})_ has not been determined!')
        if len(error_strings) > 0:
            raise gv.ErrorInStringFromUser('\n'.join(error_strings))
        return source_currency, receiver_currency, source_amount

    def get_parametrs_of_currency_convertion_by_special_rules(self, string_from_bot: str, count_right_arrow: int, count_left_arrow: int):
        str_source_currency = ''
        str_receiver_currency = ''
        str_source_amount = ''
        str_source_amount, string_from_bot = self.get_string_amount(string_from_bot)
        if count_right_arrow == 1 and count_left_arrow == 1:
            raise gv.ErrorInStringFromUser('Error! The number of parameters in the line does not match the instructions! Arrow error')
        elif count_right_arrow == 1:
            list_currency_strings = string_from_bot.split(self.__right_arrow)
            if len(list_currency_strings) != 2:
                raise gv.ErrorInStringFromUser('Error! The number of parameters in the line does not match the instructions! Currency parameters error (right arrow)')
            str_source_currency = list_currency_strings[0]
            str_receiver_currency = list_currency_strings[1]
        elif count_left_arrow == 1:
            list_currency_strings = string_from_bot.split(self.__left_arrow)
            if len(list_currency_strings) != 2:
                raise gv.ErrorInStringFromUser('Error! The number of parameters in the line does not match the instructions! Currency parameters error (left arrow)')
            str_source_currency = list_currency_strings[1]
            str_receiver_currency = list_currency_strings[0]
        else:
            raise gv.ErrorInStringFromUser('Error! The number of parameters in the line does not match the instructions! Arrow error') 
        source_currency = gv.сurrencies.get_currency_by_name(str_source_currency)
        receiver_currency = gv.сurrencies.get_currency_by_name(str_receiver_currency)
        source_amount = None
        try:
            source_amount = float(str_source_amount.replace(' ', '').replace('  ', '').replace(' ', '').replace(',', '.'))
        except ValueError:
            pass
        error_strings = []
        if source_currency is None:
            error_strings.append(f'Error! The source currency _({str_source_currency})_ has not been determined!')
        if receiver_currency is None:
            error_strings.append(f'Error! The receiver currency _({str_receiver_currency})_ has not been determined!')
        if source_amount is None:
            error_strings.append(f'Error! The source amount _({str_source_amount})_ has not been determined!')
        if len(error_strings) > 0:
            raise gv.ErrorInStringFromUser('\n'.join(error_strings))
        return source_currency, receiver_currency, source_amount

    def get_string_amount(self, string_from_bot: str):
        string_from_bot = string_from_bot.strip().strip('  ').strip(' ')
        index_left_bracket = string_from_bot.find(self.__left_bracket)
        index_right_bracket = string_from_bot.find(self.__right_bracket)
        str_source_amount = string_from_bot[index_left_bracket + 1: index_right_bracket]
        if index_left_bracket == 0:
            string_from_bot = string_from_bot[index_right_bracket + 1:]
        else:
            string_from_bot = string_from_bot[:index_left_bracket]
        return str_source_amount, string_from_bot

    def checke_paired_brackets(self, string_from_bot: str):
        stack = []  # инициализируем стек

        for s in string_from_bot:  # читаем строку посимвольно
            if s == self.__left_bracket:  # если открывающая скобка, 
                stack.append(s)  # добавляем ее в стек
            elif s == self.__right_bracket: 
                # если встретилась закрывающая скобка, то проверяем
                # пуст ли стек и является ли верхний элемент - открывающей скобкой
                if len(stack) > 0 and stack[-1] == self.__left_bracket:
                    stack.pop()  # удаляем из стека
                else:  # иначе завершаем функцию с False
                    return False
        # если стек пустой, то незакрытых скобок не осталось
        # значит возвращаем True, иначе - False
        return len(stack) == 0


    def get_string_converted_amount(self):
        currency_data_dict = {
            'ecb': {
                'method': self.get_exchange_amount_ecb,
                'thread': None,
                'value': None,
                'name': 'European Central Bank',
                'link': 'https://ecb.europa.eu/',
            },
            'xrates': {
                'method': self.get_converted_amount_xrates,
                'thread': None,
                'value': None,
                'name': 'X-Rates',
                'link': 'https://x-rates.com/',
            },
            'xe': {
                'method': self.get_converted_amount_xe,
                'thread': None,
                'value': None,
                'name': 'Xe',
                'link': 'https://xe.com/',
            },
            'yahoofin': {
                'method': self.get_converted_amount_yahoofin,
                'thread': None,
                'value': None,
                'name': 'Yahoo Finance',
                'link': 'https://yahoo.com/',
            },
            'er': {
                'method': self.get_converted_amount_er_api,
                'thread': None,
                'value': None,
                'name': 'ExchangeRate-API',
                'link': 'https://www.exchangerate-api.com/',
            },
            'cbrf': {
                'method': self.get_converted_amount_cbrf_api,
                'thread': None,
                'value': None,
                'name': 'The Central Bank of the Russian Federation',
                'link': 'https://cbr.ru/',
            },
            'cb_uzbekistan': {
                'method': self.get_converted_amount_cb_uzbekistan_api,
                'thread': None,
                'value': None,
                'name': 'The Central Bank of The Republic of Uzbekistan',
                'link': 'https://cbu.uz/',
            },
        }

        for value in currency_data_dict.values():
            thread = Thread(value['method'])
            thread.start()
            value['thread'] = thread

        for value in currency_data_dict.values():
            value['thread'].join()
            value['value'] = value['thread'].result               
        
        list_of_strings = []
        list_of_strings.append(f'*{self.__source_currency.international_designation} -> {self.__receiver_currency.international_designation}\nAmount ({self.__source_currency.international_designation}):* `{self.__source_amount}`\n')
        for key in currency_data_dict:
            data_string = ''
            if currency_data_dict[key]['value'] is None:
                data_string = '	•	The service does not process the entered currencies, or is temporarily unavailable' 
            else:
                data_string = f'	•	_Amount ({self.__receiver_currency.international_designation}):_ `{currency_data_dict[key]["value"][1]}`;\n	•	_On date:_ `{currency_data_dict[key]["value"][0]}`'
            list_of_strings.append(f'*{currency_data_dict[key]["name"]}:*\n{data_string}')
        return '\n'.join(list_of_strings)

    def processing_exceptions(func):
        def wrapper(self):
            try:
                return func(self)
            except Exception as ex:
                print()
                print('processing_exceptions', ex, func.__name__, sep = '\n')
                print()
                return None
        return wrapper

    @processing_exceptions
    def get_exchange_amount_ecb(self):
        str_source_currency = self.__source_currency.international_designation
        str_receiver_currency = self.__receiver_currency.international_designation
        currency_converter = cc()
        return datetime.today(), currency_converter.convert(self.__source_amount, str_source_currency, str_receiver_currency)

    @processing_exceptions
    def get_converted_amount_xrates(self):
        str_source_currency = self.__source_currency.international_designation
        str_receiver_currency = self.__receiver_currency.name
        today = datetime.today()
        # make the request to x-rates.com to get current exchange rates for common currencies
        content = requests.get(f"https://www.x-rates.com/table/?from={str_source_currency}&amount={self.get_source_amount_as_str()}").content
        # initialize beautifulsoup
        soup = bs(content, "html.parser")
        # get the last updated time
        price_datetime = parse(soup.find_all("span", attrs={"class": "ratesTimestamp"})[1].text)
        # get the exchange rates tables
        exchange_tables = soup.find_all("table")
        # exchange_rates = {}
        receiver_amount = 0
        for exchange_table in exchange_tables:
            for tr in exchange_table.find_all("tr"):
                # for each row in the table
                tds = tr.find_all("td")
                if tds:
                    currency = tds[0].text
                    # get the exchange rate
                    if currency.lower().strip().strip('  ').strip(' ') == str_receiver_currency.lower().strip().strip('  ').strip(' '):
                        receiver_amount = float(tds[1].text)
                        return today, receiver_amount        
        return None

    @processing_exceptions
    def get_converted_amount_xe(self):
        def get_digits_from_xe(text):
            """Returns the digits and dots only from an input `text` as a float
            Args:
                text (str): Target text to parse
            """
            new_text = ""
            for c in text:
                if c.isdigit() or c == ".":
                    new_text += c
            return float(new_text)
        str_source_currency = self.__source_currency.international_designation
        str_receiver_currency = self.__receiver_currency.international_designation
        url = f"https://www.xe.com/currencyconverter/convert/?Amount={self.get_source_amount_as_str()}&From={str_source_currency}&To={str_receiver_currency}"
        content = requests.get(url).content
        soup = bs(content, "html.parser")
        exchange_rate_html = soup.find_all("p")[2]
        # get the last updated datetime
        # last_updated_datetime = parse(re.search(r'Last updated (.+)', exchange_rate_html.parent.parent.find_all("div")[-2].text).group()[12:])
        last_updated_datetime = datetime.today()
        try:
            receiver_amount = get_digits_from_xe(exchange_rate_html.text)
        except Exception:
            return None
        return last_updated_datetime, receiver_amount
  
    @processing_exceptions
    def get_converted_amount_yahoofin(self):
        str_source_currency = self.__source_currency.international_designation
        str_receiver_currency = self.__receiver_currency.international_designation
        # construct the currency pair symbol
        symbol = f"{str_source_currency}{str_receiver_currency}=X"
        # extract minute data of the recent 2 days
        latest_data = si.get_data(symbol, interval="1m", start_date=datetime.now() - timedelta(days=2))
        if latest_data is None:
            return None
        # get the latest datetime
        last_updated_datetime = latest_data.index[-1].to_pydatetime()
        # get the latest price
        latest_price = latest_data.iloc[-1].close
        # return the latest datetime with the converted amount
        return last_updated_datetime, latest_price * self.__source_amount

    @processing_exceptions
    def get_converted_amount_er_api(self):
        def convert_currency_erapi(amount, exchange_rates, str_receiver_currency):
            return exchange_rates[str_receiver_currency] * amount

        str_source_currency = self.__source_currency.international_designation
        str_receiver_currency = self.__receiver_currency.international_designation
        url = f"https://open.er-api.com/v6/latest/{str_source_currency}"
        # request the open ExchangeRate API and convert to Python dict using .json()
        data = requests.get(url).json()
        if data["result"] == "success":
            # request successful
            # get the last updated datetime
            last_updated_datetime = parse(data["time_last_update_utc"])
            # get the exchange rates
            exchange_rates = data["rates"]
        return last_updated_datetime, convert_currency_erapi(self.__source_amount, exchange_rates,  str_receiver_currency)

    @processing_exceptions
    def get_converted_amount_cbrf_api(self):
        return self.get_converted_amount_from_bank('RUB')

    @processing_exceptions
    def get_converted_amount_cb_uzbekistan_api(self):
        return self.get_converted_amount_from_bank('UZS')

    def get_converted_amount_from_bank(self, str_main_currency: str):
        def check_filling_of_currency_data(source_currency_exchange_rate, receiver_currency_exchange_rate, source_currency_denomination, receiver_currency_denomination):
            if source_currency_exchange_rate is None \
                or receiver_currency_exchange_rate is None \
                or source_currency_denomination is None \
                or receiver_currency_denomination is None:
                return False
            else:
                return True
        main_currency = gv.сurrencies.get_currency_by_name(str_main_currency)
        str_source_currency = self.__source_currency.international_designation
        str_receiver_currency = self.__receiver_currency.international_designation
        source_currency_exchange_rate = None
        receiver_currency_exchange_rate = None
        source_currency_denomination = None
        receiver_currency_denomination = None
        main_currency_amount = 0
        if self.__source_currency == main_currency:
            source_currency_exchange_rate = 1
            source_currency_denomination = 1
        elif self.__receiver_currency == main_currency:
            receiver_currency_exchange_rate = 1
            receiver_currency_denomination = 1
        today = datetime.today()
        if str_main_currency == 'UZS':
            str_today = today.strftime('%Y-%m-%d')
            url = f"https://cbu.uz/ru/arkhiv-kursov-valyut/json/all/{str_today}/"
            content = requests.get(url).content
            currencies_from_bank = json.loads(content)
            for currency in currencies_from_bank:
                if str_source_currency == currency['Ccy'] \
                    and source_currency_exchange_rate is None:
                    source_currency_exchange_rate = float(currency['Rate'])
                    source_currency_denomination = float(currency['Nominal'])
                elif str_receiver_currency == currency['Ccy'] \
                    and receiver_currency_exchange_rate is None:
                    receiver_currency_exchange_rate = float(currency['Rate'])
                    receiver_currency_denomination = float(currency['Nominal'])
                if check_filling_of_currency_data(source_currency_exchange_rate, receiver_currency_exchange_rate, source_currency_denomination, receiver_currency_denomination):
                    break
            if not check_filling_of_currency_data(source_currency_exchange_rate, receiver_currency_exchange_rate, source_currency_denomination, receiver_currency_denomination):
                return None
        elif str_main_currency == 'RUB':
            daily = DailyCurrenciesRates()  
            daily.date = today
            for rates in daily.rates:
                currency = daily.get_by_id(rates)
                if str_source_currency == currency.char_code \
                    and source_currency_exchange_rate is None:
                    source_currency_exchange_rate = float(currency.value)
                    source_currency_denomination = currency.denomination
                elif str_receiver_currency == currency.char_code \
                    and receiver_currency_exchange_rate is None:
                    receiver_currency_exchange_rate = float(currency.value)
                    receiver_currency_denomination = currency.denomination
                if check_filling_of_currency_data(source_currency_exchange_rate, receiver_currency_exchange_rate, source_currency_denomination, receiver_currency_denomination):
                    break
            if not check_filling_of_currency_data(source_currency_exchange_rate, receiver_currency_exchange_rate, source_currency_denomination, receiver_currency_denomination):
                return None
        else:
            raise ValueError('Invalid string value of main currency was passed!')
        main_currency_amount = self.__source_amount * source_currency_exchange_rate / source_currency_denomination
        receiver_amount = main_currency_amount / receiver_currency_exchange_rate * receiver_currency_denomination
        return today, receiver_amount

    def get_source_amount_as_str(self, sep = '.'):
        if sep == '.':
            return str(self.__source_amount).replace(' ', '').replace(' ', '')
        else:
            return str(self.__source_amount).replace('.', sep).replace(' ', '').replace(' ', '')

    @staticmethod
    def get_price(base, quote, amount): # In order to fulfill a task condition. This method is not used. The assignment does not say that I should use this method
        my_currency_converter = MyCurrencyConverter('', {
            'base': gv.сurrencies.get_currency_by_name(base),
            'quote': gv.сurrencies.get_currency_by_name(quote),
            'amount': float(amount),
        })
        result = my_currency_converter.get_converted_amount_cb_uzbekistan_api()
        if not result is None:
            return result[1] 
        return None
        