import threading

def thread(function):
    return lambda *args,**kwargs:threading.Thread(target=function,args=args,kwargs=kwargs).start()