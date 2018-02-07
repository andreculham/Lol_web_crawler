from django.apps import AppConfig

class Dynamic(object):
    pass
class MainConfig(AppConfig):
    name = 'main'
    def ready(self):
        from main.apicaller import ApiCaller
        obj = Dynamic()
        obj.name = "Starting Thread"
        obj.region = "NA1"
        obj.objType = "match"
        t = ApiCaller(obj)
        obj2 = Dynamic()
        obj2.name = "Starting Thread 2"
        obj2.region = "jp1"
        obj2.objType = "match"
        t2 = ApiCaller(obj2)
        t.daemon = True
        t2.daemon= True
        t.start()
        t2.start()
        #t.event.set()  #stopping the thread
        #t2.event.set()
    
    
    


        

