import time
import json
from django.http import HttpResponse
from django.template import loader
from .models import Match
from .models import SummonerDTO
from .models import ChampionMasteryDTO
from .models import ChampionDto
from riotwatcher import RiotWatcher
from django.core import serializers
from requests import HTTPError
import threading
from main.apicaller import ApiCaller
import gc
from django.shortcuts import render


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


def api_caller(latest_match_id):    
    watcher = RiotWatcher('RGAPI-bdf0d7e8-4bfe-4386-983e-78ba3767e454')
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
    
def search(request, search_value):
    ## search in database
    watcher = RiotWatcher('RGAPI-bdf0d7e8-4bfe-4386-983e-78ba3767e454')
    region = 'na1'

    # sudo code

    # summoner_info = SummonerDTO where name matches search_value


    # league info

    # summoner_league = 'Unranked'
    # points = 0
    # wins = 0
    # losses = 0
    # try_league = watcher.league.positions_by_summoner(region, summoner_id)
    # if (try_league != []):
    #     leagues = try_league[0]
    #     summoner_league = leagues['tier'] + ' ' + leagues['rank']
    #     points = leagues['leaguePoints']
    #     wins = leagues['wins']
    #     losses = leagues['losses']
    #
    #     if losses == 0:
    #         if wins == 0:
    #             rate = 0
    #         else:
    #             rate = 100
    #     else:
    #         rate = round(float(wins) / float(wins + losses) * 100, 2)

    # match list
    # need to store the list of recent matches in database



    # return render(request, 'main\\search.html', {'search_value':search_value,
    #                                        'summoner_info': summoner_info,
    #                                        'name': summoner_info['name'],
    #                                        'icon': summoner_info['profileIconId'],
    #                                        'league': summoner_league,
    #                                        'points': points,
    #                                        'level': summoner_info['summonerLevel'],
    #                                        'wins': wins,
    #                                        'losses': losses,
    #                                        'rate': rate,
    #                                        'match_list': match_list})


    return update(request, search_value)

def home(request):
    return render(request,'main\\search.html')


def update(request, search_value):
    watcher = RiotWatcher('RGAPI-bdf0d7e8-4bfe-4386-983e-78ba3767e454')
    region = 'na1'
    with open("main\\static\\chamList.txt") as json_data:
        chamList = json.load(json_data)
    ## handle non english name
    try:
        name = search_value.replace("%20", " ")

        #summoner info
        summoner_info = watcher.summoner.by_name(region, name)
        acc_id = summoner_info["accountId"]
        summoner_id = str(summoner_info['id'])
        name = summoner_info["name"]

        print("######### summoner info #########")
        print(name)
        #match info
        match_list = []
        matchlist = watcher.match.matchlist_by_account_recent(region, acc_id)
        print("##### matchlist #####")
        print(matchlist['matches'])
        for match in matchlist['matches']:
            matchId = match['gameId']
            match_detail = watcher.match.by_id(region, matchId)

            participantId = [participant['participantId'] for participant in match_detail['participantIdentities'] if
                             participant['player']['summonerName'] == name][0]

            participant = [participant for participant in match_detail['participants'] if
                           participant['participantId'] == participantId][0]

            itemkeys = ['item0', 'item1', 'item2', 'item3', 'item4', 'item5', 'item6']
            items = [participant['stats'][key] for key in itemkeys]
            for item in items:
                if item=='0':
                    item = '3637'
            doublekill = participant['stats']['doubleKills'] > 0
            triplekill = participant['stats']['tripleKills'] > 0
            quadrakill = participant['stats']['quadraKills'] > 0
            pentakill = participant['stats']['pentaKills'] > 0
            cId = participant['championId']


            game_type = 'NA'


            champion = chamList[str(cId)]
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
                               'gameType': game_type,
                               'match': match,
                               'matchDetail': match_detail})
        print("######### match info #########")
        print(match_list == [])
        #league info
        summoner_league = 'Unranked'
        points = 0
        wins = 0
        losses = 0
        try_league = watcher.league.positions_by_summoner(region, summoner_id)
        if (try_league != []):
            leagues = try_league[0]
            summoner_league = leagues['tier'] + ' ' + leagues['rank']
            points = leagues['leaguePoints']
            wins = leagues['wins']
            losses = leagues['losses']

            if losses == 0:
                if wins == 0: rate = 0
                else: rate = 100
            else:
                rate = round(float(wins)/float(wins+losses)*100, 2)
        print("######### league info #########")
        print(summoner_league)
    except Exception as err:
        print('This is the error')
        print(str(err))

    return render(request, 'main\\search.html', {'search_value':search_value,
                                           'summoner_info': summoner_info,
                                           'name': summoner_info['name'],
                                           'icon': summoner_info['profileIconId'],
                                           'league': summoner_league,
                                           'points': points,
                                           'level': summoner_info['summonerLevel'],
                                           'wins': wins,
                                           'losses': losses,
                                           'rate': rate,
                                           'match_list': match_list})