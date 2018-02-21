import time
import json
from django.http import HttpResponse
from django.template import loader
from .models import Match, SummonerDTO
from riotwatcher import RiotWatcher
from django.core import serializers
from requests import HTTPError
import threading
from main.apicaller import ApiCaller
import gc
import main.summoner

class Dynamic(object):
    pass
def index(request):
    obj_list= []
    for obj in gc.get_objects():
        if isinstance(obj, ApiCaller):
            obj_list.append(obj)
    if len(request.body) > 0:
        if 'add' in request.POST:
            obj = Dynamic()
            obj.region = request.POST['platformId']
            obj.name = request.POST['threadName']
            obj.objType = request.POST['objType']
            obj_list.append(obj)
            t = ApiCaller(obj)
            t.daemon = True
            t.start()
        elif 'remove' in request.POST:
            i = request.POST['remove']
            index = int(i[-1:]) - 1
            print(obj_list[index].getName() +' has been stopped')
            obj_list[index].event.set()
            del obj_list[index]
    #threads = threading.enumerate()
    template = loader.get_template('main/index.html')
    region_list = ['RU', 'KR', 'BR1', 'OC1', 'JP1', 'NA1', 'EUN1', 'EUW1', 'TR1', 'LA1', 'LA2']
    objTypes = ['Match', 'Summoner']
    context = {
        'regions' : region_list,
        'objTypes' : objTypes,
        'obj_list' : obj_list,
        'selected' : 'JP1'
    }
    return HttpResponse(template.render(context, request))

def workload(request):
    if len(request.body) > 0:
        match_list = Match.objects.all()
        template = loader.get_template('main/workload.html')
        start_time = request.POST['startTime']
        end_time = request.POST['endTime']
        filtered_match_list = []
        for match in match_list:
            match.gameCreation = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(match.gameCreation/1000.0))
            match.participantIdentities = len(match.participantIdentities)
            if(match.gameCreation > start_time and match.gameCreation < end_time):
                filtered_match_list.append(match)
        context = {
            'total_match_len' : Match.objects.all().count(),
            'match_list' : filtered_match_list
        }
    else:
        match_list_len = Match.objects.all().count()
        template = loader.get_template('main/workload.html')
        context = {
            'total_match_len' : match_list_len,
        }
    return HttpResponse(template.render(context, request))

def home(request):
    template = loader.get_template('main/search.html')
    context={
        }
    return HttpResponse(template.render(context, request))
def search(request, search_value):
    print("############# Searching........ #############")
    search_value = search_value.replace("%20", " ")
    #summoner_info = models.search_by_name(search_value)
    #summoner_info = SummonerDTO.objects.filter(name=search_value)
    summoner_info = main.summoner.search_by_name(search_value)
    print("############# Return Summoner Info #############")
    print(summoner_info)
    match_list = []
    #client = MongoClient()
    #chamList = client.test
    for match in summoner_info['matchlist']['matches']:
        participantId = [participant['participantId'] for participant in match['detail']['participantIdentities'] if
                         participant['player']['summonerName'] == summoner_info['name']][0]
        participant = [participant for participant in match['detail']['participants'] if
                       participant['participantId'] == participantId][0]
        itemkeys = ['item0','item1','item2','item3','item4','item5','item6']
        items = [participant['stats'][key] for key in itemkeys]
        doublekill = participant['stats']['doubleKills'] > 0
        triplekill = participant['stats']['tripleKills'] > 0
        quadrakill = participant['stats']['quadraKills'] > 0
        pentakill = participant['stats']['pentaKills'] > 0
        cId = participant['championId']
        game_type = match['detail']['gameMode']
        #cursor = chamList.champions.find({'id':cId})
        #champion = [doc['key'] for doc in cursor][0]
        champion = ''
        match_list.append({'champion': champion,
                           'kills': participant['stats']['kills'],
                           'deaths': participant['stats']['deaths'],
                           'assists': participant['stats']['assists'],
                           'win': participant['stats']['win'],
                           'level': participant['stats']['champLevel'],
                           'items': items,
                           'penta': pentakill,
                           'quadra': quadrakill,
                           'triple': triplekill,
                           'double': doublekill,
                           'gameType':game_type,
                           'match': match})
        #print(match)
    losses = summoner_info['league']['losses']
    wins = summoner_info['league']['wins']
    if losses == 0:
        if wins == 0: rate = 0
        else: rate = 100
    else:
        rate = round(float(wins)/float(wins+losses)*100, 2)
    template = loader.get_template('main/search.html')
    context = {'search_value':search_value,
            'summoner_info': summoner_info,
            'name': summoner_info['name'],
            'icon': summoner_info['profileIconId'],
            'league': summoner_info['league']['league'],
            'points': summoner_info['league']['points'],
            'level': summoner_info['summonerLevel'],
            'wins': wins,
            'losses': losses,
            'rate': rate,
            'match_list': match_list}
    return HttpResponse(template.render(context, request))

def api_caller(latest_match_id):    
    watcher = RiotWatcher('RGAPI-a8c42df2-8906-410f-b185-4af067244a93')
    region = 'jp1'
    i= latest_match_id
    while 1:
        try:
            response = watcher.match.by_id(region, i)
            print("calling match id: {}".format(i))
            data = {} 
            data['model'] = "main.match"
            data['pk'] = i
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
                print(err)
        i += 1
    
