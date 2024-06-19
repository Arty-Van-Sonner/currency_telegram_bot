import threading

import global_variables as gv

class Thread(threading.Thread):
    '''
    
    '''
    __method = None
    __result = None
    def __init__(self, method) -> None:
        threading.Thread.__init__(self)
        self.__method = method

    def run(self):
        self.__result = self.__method()

    @property
    def result(self):
        return self.__result
        