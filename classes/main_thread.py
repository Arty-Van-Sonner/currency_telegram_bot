import global_variables as gv

class MainThread:
    '''
    Class MainThread creat object main thread 'with' direction:
    Fields:
        
        ...

    Methods:
        __init__ - None - class constructor
        __enter__ - <class 'MainThread'> - method call direction 'with' and return this object
        __exit__ - None - method executed at the end of the code in the body of the 'with' directive. It changes trigger __main_thread_is_live in currencies  
    '''
    def __init__(self) -> None:
        '''
        self - <class 'MainThread'> - object of this class
        '''
        pass

    def __enter__(self):
        '''
        self - <class 'MainThread'> - object of this class
        '''
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        '''
        self - <class 'MainThread'> - object of this class
        exc_type - <class '[exeptions]'> - type of exeptions in case of an emergency shutdown of the program
        exc_val - str - description of exeption reason in case of an emergency shutdown of the program
        exc_tb - object - the object of the message from the interpreter
        '''
        gv.сurrencies.main_thread_is_dead()
        