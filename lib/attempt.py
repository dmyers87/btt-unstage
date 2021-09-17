from typing import Callable


class Attempt():
    handlers = []
    
    def __init__(self, action: Callable, pre_msg: str, success_msg: str, **kwargs):
        self.action = action
        self.pre_msg = pre_msg
        self.success_msg = success_msg
        self.action_args = kwargs

    def add_exception_handler(self, exception_type: object, failure_msg: str = None, handler: Callable = None):
        self.handlers.append((exception_type, handler, failure_msg))
    
    def execute(self):
        if self.pre_msg:
            print(self.pre_msg)
        try:
            self.action(**self.action_args)
            if self.success_msg:
                print(self.success_msg)
        except Exception as error:
            for exception_type, handler, failure_msg in self.handlers:
                if error.__class__ == exception_type:
                    if failure_msg:
                        print(failure_msg)
                    if handler:
                        handler(error)
            
                    




    

