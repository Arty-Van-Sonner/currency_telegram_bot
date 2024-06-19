import sqlite3 as sql

import global_variables as gv

class SQLite:
    '''
    Class SQLite help to connect SQLite3 database:
    Fields:
        __connect - <class 'sqlite3.Connection'> - connect to the SQLite3 database
        __cursor - <class 'sqlite3.Cursor'> - cursor for interaction with the SQLite3 database 
        __file_name - str - database file name
        __is_connected - bool - database connected trigger
    Methods:
        __init__ - None - class constructor
        __to_connect - None - method connect to database, creat cursor
        __enter__ - <class 'SQLite'> - method call direction 'with' and return this object
        __exit__ - None - method executed at the end of the code in the body of the 'with' directive. It will close connect with database
        get_currency - dict - method return currency data from database
        get_currencies_id - list[int] - method return list of currencies id
        updated_at - str - method-property return last update time from database  
    '''
    __connect: sql.Connection
    __cursor: sql.Cursor
    __file_name: str
    __is_connected: bool

    def __init__(self, file_name) -> None:
        '''
        self - <class 'SQLite'> - object of this class
        file_name - str - database file name
        '''
        self.__file_name = file_name
        self.__is_connected = False

    def __to_connect(self) -> None:
        '''
        self - <class 'SQLite'> - object of this class
        '''
        self.__connect = sql.connect(self.__file_name)
        try:
            self.__connect.row_factory = sql.Row
            self.__cursor = self.__connect.cursor()
            self.__is_connected = True
        except Exception:
            pass

    def __enter__(self):
        '''
        self - <class 'SQLite'> - object of this class
        '''
        self.__to_connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        '''
        self - <class 'SQLite'> - object of this class
        exc_type - <class '[exeptions]'> - type of exeptions in case of an emergency shutdown of the program
        exc_val - str - description of exeption reason in case of an emergency shutdown of the program
        exc_tb - object - the object of the message from the interpreter
        '''
        self.__connect.close()
        

    def get_currency(self, currency) -> dict:
        '''
        self - <class 'SQLite'> - object of this class
        currency - <class 'Currency'> - currency object
        '''
        if not self.__is_connected or type(self.__cursor) != sql.Cursor:
            raise gv.ErrorConnectionSQLite('')
        reqest_parametrs_dict = {'id': currency._id}
        self.__cursor.execute(
            '''
            SELECT
                cur.code_currency as code,
                cur.international_designation as international_designation,
                cur.name as name,
                cur.country as country
            FROM
                currencies as cur
            WHERE
                cur.id = :id
            ''',
            reqest_parametrs_dict
        )
        result = self.__cursor.fetchall()
        result_dict = {}
        for row in result:
            for key in row.keys():
                result_dict.update({key: row[key]})
        self.__cursor.execute(
            '''
            SELECT
                cno.name as name
            FROM
                currency_name_options as cno
            WHERE
                cno.currency_id = :id
            ''',
            reqest_parametrs_dict
        )
        result = self.__cursor.fetchall()
        currency_name_options = []
        for row in result:
            currency_name_options.append(row['name'])
        result_dict.update({'currency_name_options': currency_name_options})
        return result_dict

    def get_currencies_id(self) -> list[int]:
        '''
        self - <class 'SQLite'> - object of this class
        '''
        if not self.__is_connected or type(self.__cursor) != sql.Cursor:
            raise gv.ErrorConnectionSQLite('')
        self.__cursor.execute(
            '''
            SELECT
                cur.id as id
            FROM
                currencies as cur
            ORDER BY
                id 
            '''
        )
        result = self.__cursor.fetchall()
        currencies_id = []
        for row in result:
            currencies_id.append(row['id'])
        return currencies_id

    @property
    def updated_at(self) -> str:
        '''
        self - <class 'SQLite'> - object of this class
        '''
        self.__cursor.execute(
            '''
            SELECT
                updates.updated_at as updated_at
            FROM
                updates as updates
            WHERE
                updates.id = 1
            '''
        )
        result = self.__cursor.fetchall()
        updated_at = None
        for row in result:
            updated_at = row['updated_at']
        return updated_at   
