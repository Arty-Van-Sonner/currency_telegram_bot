from time import sleep
from datetime import datetime

from sqlite import SQLite
import global_variables as gv

class Currencies:
    '''
    Class Currencies save data about all currencies and update them from database:
    Fields:
        __data_dict - dict - saving all currencies by id
        __main_thread_is_live - bool - main thread live trigger
        __updated_at - str - date of last update of data in database
    Methods:
        __init__ - None - class constructor
        update_currencies - None - method update all currencies data
        get_currency_by_name - <class 'Currency'>, None - method return currency by string. If currency didn't locate, method return None
        constant_update_processing - None - method constant update currency data from database
        main_thread_is_dead - None - method change value of __main_thread_is_live to False
        list_currencies_for_output - str - method-property return list of all currencies
    '''
    __data_dict: dict
    __main_thread_is_live: bool
    __updated_at: str
    
    def __init__(self) -> None:
        '''
        self - <class 'Currencies'> - object of this class
        '''
        self.__data_dict = {}
        self.__main_thread_is_live = True
    
    def update_currencies(self) -> None:
        '''
        self - Currencies - object of this class
        '''
        from currency import Currency
        list_of_currencies_id = gv.database.get_currencies_id()
        for currency_id in list_of_currencies_id:
            currency = self.__data_dict.get(currency_id)
            if currency is None:
                self.__data_dict.update({currency_id: Currency(currency_id)})
            else:
                currency.update_currency()
        self.__updated_at = gv.database.updated_at

    def get_currency_by_name(self, currency_name: str):
        '''
        self - <class 'Currencies'> - object of this class
        currency_name - str - name of currency that you want to get. If currency didn't locate, method return None 
        '''
        for key in self.__data_dict:
            currency = self.__data_dict[key].get_currency_by_name_option(currency_name)
            if not currency is None:
                return currency
        return None

    def constant_update_processing(self) -> None:
        '''
        self - <class 'Currencies'> - object of this class
        '''
        with SQLite('database.db') as sql:
            gv.database = sql
            self.update_currencies()
            while self.__main_thread_is_live:
                updated_at = gv.database.updated_at
                if self.__updated_at != updated_at:
                    self.update_currencies()
                    print()
                    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++') 
                    print(f'The last update in the database was in {updated_at}')
                    print(f'Updating the data in the program in {datetime.now()}')
                    print('--------------------------------------------------------')
                    print()
                sleep(60)    

    def main_thread_is_dead(self) -> None:
        '''
        self - <class 'Currencies'> - object of this class
        '''
        print()
        print('Shutdown! Wait until all application threads are closed!')
        print()
        self.__main_thread_is_live = False

    @property
    def list_currencies_for_output(self) -> str:
        '''
        self - <class 'Currencies'> - object of this class
        '''
        result_str = ''
        for currency in self.__data_dict.values():
            result_str += f'\n•	{currency.name} ({currency.international_designation})'
        return result_str
