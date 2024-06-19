import global_variables as gv

class Currency:
    '''
    Class Currency save all data about currency and update it from database:
    Fields:
        __id - int - id currency from database
        __code - int - international code of currency
        __international_designation - str - international short name of currency
        __name - str - english name of currency
        __country - str - country(s) of currency
        __currency_name_options - list[str] - list of name that you can use through bot
    Methods:
        __init__ - None - class constructor
        __eq__ - bool - method provides a comparison of two objects (Currency class) with the equal (==) operator
        update_currency - None - method update currency data
        get_currency_by_name_option - Currency, None - method return currency by string. If currency didn't locate, method return None
        _id - int - method-property return currency id
        code - int - method-property return currency code
        name - str - method-property return currency name
        international_designation - str - method-property return international short currency name
        country - str - method-property return country(s) of currency
        currency_name_options - list[str] - method-property return currency option name
        description - str - method-property return all currency description 
    '''
    __id: int
    __code: int
    __international_designation: str
    __name: str
    __country: str
    __currency_name_options: list[str]
    
    def __init__(self, _id: int) -> None:
        '''
        self - <class 'Currency'> - object of this class
        id - int - id currency from database
        '''
        self.__id = _id
        self.update_currency()

    def __eq__(self, __object: object) -> bool:
        '''
        self - <class 'Currency'> - object of this class
        __object - <class 'Currency'> - another object of class Currency for comparison
        '''
        result = False
        if type(__object) != Currency:
            return result
        if self.__id == __object.__id \
            and self.__international_designation == __object.__international_designation \
            and self.__code == __object.__code:
            result = True  
        return result

    def update_currency(self) -> None:
        '''
        self - <class 'Currency'> - object of this class
        '''
        update_dict = gv.database.get_currency(self)
        for property in update_dict:
            if not update_dict[property] is None:
                if  property == 'code':
                    self.__code = update_dict[property]
                elif property == 'international_designation':
                    self.__international_designation = update_dict[property]
                elif property == 'name':
                    self.__name = update_dict[property]
                elif property == 'country':
                    self.__country = update_dict[property]
                elif property == 'currency_name_options':
                    self.__currency_name_options = update_dict[property]     

    def get_currency_by_name_option(self, name_option: str):
        '''
        self - <class 'Currency'> - object of this class
        name_option - str - currency option name
        '''
        for name in self.__currency_name_options:
            corect_name = name.lower().strip().strip('  ').strip(' ')
            corect_name_option = name_option.lower().strip().strip('  ').strip(' ')
            corect_name_with_ = corect_name.replace(' ', '_')
            corect_name_option_with_ = corect_name_option.replace(' ', '_')
            if corect_name == corect_name_option \
                or corect_name_with_ == corect_name_option_with_:
                return self
        return None

    @property  
    def _id(self) -> int:
        '''
        self - <class 'Currency'> - object of this class
        '''
        return self.__id

    @property
    def code(self) -> int:
        '''
        self - <class 'Currency'> - object of this class
        '''
        return self.__code

    @property
    def name(self) -> str:
        '''
        self - <class 'Currency'> - object of this class
        '''
        return self.__name

    @property
    def international_designation(self) -> str:
        '''
        self - <class 'Currency'> - object of this class
        '''
        return self.__international_designation

    @property
    def country(self) -> str:
        '''
        self - <class 'Currency'> - object of this class
        '''
        return self.__country
    
    @property
    def currency_name_options(self) -> list[str]:
        '''
        self - <class 'Currency'> - object of this class
        '''
        return self.__currency_name_options

    @property
    def description(self):
        '''
        self - <class 'Currency'> - object of this class
        '''
        description = f'''*Currency {self.name} ({self.international_designation})*:
    •	*International code:* {self.code};
    •	*Name:* {self.name};
    •	*International designation:* {self.international_designation};
    •	*Country:* {self.country}
    •	*Currency name options:* {self.currency_name_options}'''
        return description
        