from riotwatcher import RiotWatcher
import time
import json
from main.models import Match
from django.core import serializers
from requests import HTTPError
from threading import Thread
import threading
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)

class ApiCaller(threading.Thread):
    def __init__(self, obj):
        threading.Thread.__init__(self)
        self.lock = threading.RLock()
        self.name = obj.name
        self.region = obj.region
        self.objType = obj.objType
        self.event = threading.Event()
    def run(self):
        watcher = RiotWatcher('RGAPI-037a581d-1a62-4dc6-9040-f6de10e853bf')
        region = self.region
        i= 2585564750
        while not self.event.is_set():
            logging.debug('Waiting for a lock')
            self.lock.acquire()
            #last object for platform id
            #obj = Match.objects.latest('gameId')
            #i = obj.gameId + 1
        
            try:
                response = watcher.match.by_id(region, i)
                #print(response)
                log = self.getName() + ' ' + self.objType + ' id: ' + str(i)
                print(log)
                data = {} 
                data['model'] = "main." + self.objType
                #data['pk'] = 
                data['fields'] = response
                data = [data]
                data = json.dumps(data, ensure_ascii=False)
                for deserialized_object in serializers.deserialize("json", data):
                    deserialized_object.save()
            except HTTPError as err:
                if err.response.status_code == 403:
                    print('API Key is invalid or has expired')
                    break
                else:
                    print(self.getName() + ' ' +str(err))
            finally:
                logging.debug('Released a lock')
                self.lock.release()           
            i += 1
