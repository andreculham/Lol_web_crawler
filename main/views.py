import time
import json
from django.http import HttpResponse
from django.template import loader
from .models import Match
from .models import SummonerDTO
from .models import ChampionMasteryDTO
from .models import ChampionDto
from .models import LeaguePositionDTO
from riotwatcher import RiotWatcher
from django.core import serializers
from requests import HTTPError
import threading
from main.apicaller import ApiCaller
import gc
from django.shortcuts import render
import datetime

import random
import psycopg2


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
    watcher = RiotWatcher('RGAPI-c9b71261-6f44-46df-8fb4-16d977e9411a')
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
    
def search(request, search_value, region="NA1"):
    watcher = RiotWatcher('RGAPI-c9b71261-6f44-46df-8fb4-16d977e9411a')
    reg = region
    ## search in database
    chamList = {"1": "Annie", "2": "Olaf", "3": "Galio", "516": "Ornn", "5": "XinZhao",
                "6": "Urgot", "7": "Leblanc", "8": "Vladimir", "9": "Fiddlesticks", "10": "Kayle",
                "11": "MasterYi", "12": "Alistar", "13": "Ryze", "14": "Sion", "15": "Sivir",
                "16": "Soraka", "17": "Teemo", "18": "Tristana", "19": "Warwick", "20": "Nunu",
                "21": "MissFortune", "22": "Ashe", "23": "Tryndamere", "24": "Jax", "4": "TwistedFate",
                "26": "Zilean", "27": "Singed", "28": "Evelynn", "29": "Twitch", "30": "Karthus",
                "31": "Chogath", "32": "Amumu", "33": "Rammus", "34": "Anivia", "35": "Shaco",
                "36": "DrMundo", "37": "Sona", "38": "Kassadin", "39": "Irelia", "40": "Janna",
                "41": "Gangplank", "42": "Corki", "43": "Karma", "44": "Taric", "45": "Veigar",
                "48": "Trundle", "50": "Swain", "51": "Caitlyn", "53": "Blitzcrank", "54": "Malphite",
                "55": "Katarina", "56": "Nocturne", "57": "Maokai", "58": "Renekton", "59": "JarvanIV",
                "60": "Elise", "61": "Orianna", "62": "MonkeyKing", "63": "Brand", "64": "LeeSin",
                "67": "Vayne", "68": "Rumble", "69": "Cassiopeia", "72": "Skarner", "74": "Heimerdinger",
                "75": "Nasus", "76": "Nidalee", "77": "Udyr", "78": "Poppy", "79": "Gragas",
                "80": "Pantheon", "81": "Ezreal", "82": "Mordekaiser", "83": "Yorick", "84": "Akali",
                "85": "Kennen", "86": "Garen", "89": "Leona", "90": "Malzahar", "91": "Talon", "92": "Riven",
                "96": "KogMaw", "98": "Shen", "99": "Lux", "101": "Xerath", "102": "Shyvana",
                "103": "Ahri", "104": "Graves", "105": "Fizz", "106": "Volibear", "107": "Rengar",
                "110": "Varus", "111": "Nautilus", "112": "Viktor", "113": "Sejuani", "114": "Fiora",
                "115": "Ziggs", "117": "Lulu", "119": "Draven", "120": "Hecarim", "121": "Khazix",
                "122": "Darius", "126": "Jayce", "127": "Lissandra", "131": "Diana", "133": "Quinn",
                "134": "Syndra", "136": "AurelionSol", "141": "Kayn", "142": "Zoe", "143": "Zyra",
                "150": "Gnar", "25": "Morgana", "154": "Zac", "157": "Yasuo", "161": "Velkoz",
                "163": "Taliyah", "164": "Camille", "201": "Braum", "202": "Jhin", "203": "Kindred",
                "222": "Jinx", "223": "TahmKench", "236": "Lucian", "238": "Zed", "240": "Kled", "245": "Ekko",
                "254": "Vi", "266": "Aatrox", "267": "Nami", "268": "Azir", "412": "Thresh", "420": "Illaoi",
                "421": "RekSai", "427": "Ivern", "429": "Kalista", "432": "Bard", "497": "Rakan", "498": "Xayah"}
    type_dict = {400: 'Draft Pick',
                 420: 'Ranked Solo',
                 430: 'Blind Pick',
                 440: 'Ranked Flex',
                 450: 'ARAM',
                 460: '3v3 Blind Pick',
                 470: '3v3 Ranked Flex',
                 900: 'ARURF'}

    try:
        name = search_value.replace("%20", " ")
        # summoner info
        summoner_info = watcher.summoner.by_name(region, name)
        acc_id = summoner_info["accountId"]
        summoner_id = str(summoner_info['id'])
        name = summoner_info["name"]
        summoner = SummonerDTO.objects.get(id=summoner_id)

        matchlist=summoner.matchList
        analysis=summoner.analysis

        # print matchlist
        # print analysis
        match_list=[]
        for match in matchlist['matches']:
            matchId = match['gameId']

            #time
            time = datetime.datetime.fromtimestamp(match['timestamp']/1000).strftime('%Y-%m-%d %H:%M:%S')

            #game type
            try:
                type = type_dict[match['queue']]
            except Exception as error:
                type = 'Unusual'

            #detail
            match_detail = Match.objects.get(gameId=matchId)
            print match_detail.participantIdentities
            participantId = [participant['participantId'] for participant in match_detail.participantIdentities if
                             participant['player']['summonerName'] == name][0]

            participant = [participant for participant in match_detail.participants if
                           participant['participantId'] == participantId][0]

            team_size = len(match_detail.participantIdentities) / 2

            itemkeys = ['item0', 'item1', 'item2', 'item3', 'item4', 'item5', 'item6']
            items = []
            for key in itemkeys:
                item = participant['stats'][key]

                if item == 0:
                    item = 3637
                items.append(item)

            doublekill = participant['stats']['doubleKills'] > 0
            triplekill = participant['stats']['tripleKills'] > 0
            quadrakill = participant['stats']['quadraKills'] > 0
            pentakill = participant['stats']['pentaKills'] > 0
            cId = participant['championId']

            champion = chamList[str(cId)]

            duration = datetime.datetime.fromtimestamp(match_detail.gameDuration).strftime('%M:%S')

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
                               'gameType': type,
                               'teamSize': team_size,
                               'time': time,
                               'duration': duration,
                               'match': match,
                               'matchDetail': match_detail})

        #league info

        try:
            try_league = LeaguePositionDTO.objects.get(playerOrTeamId=summoner_id)

            summoner_league = try_league.tier + ' ' + try_league.rank
            points = try_league.leaguePoints
            wins = try_league.wins
            losses = try_league.losses
        except Exception as e:
            summoner_league = 'Unranked'
            points = 0
            wins = 0
            losses = 0

        if losses == 0:
            if wins == 0: rate = 0
            else: rate = 100
        else:
            rate = round(float(wins)/float(wins+losses)*100, 2)

        #champion mastery
        mastery_list = watcher.champion_mastery.by_summoner(region,summoner_id)
        for mast in mastery_list:
            mast['champion'] = chamList[str(mast['championId'])]


        return render(request, 'main\\search.html', {
                                               'region': reg,
                                               'search_value':search_value,
                                               'summoner_info': summoner_info,
                                               'name': summoner_info['name'],
                                               'icon': summoner_info['profileIconId'],
                                               'league': summoner_league,
                                               'points': points,
                                               'level': summoner_info['summonerLevel'],
                                               'wins': wins,
                                               'losses': losses,
                                               'rate': rate,
                                               'match_list': match_list,
                                               'mastery_list': mastery_list,
                                               'analysis':analysis,
                                               'error':False,
                                               'notfound':False})
    except (SummonerDTO.DoesNotExist,Match.DoesNotExist) as e:
        return render(request, "main\\search.html", {'error': False,'notfound':True,'region': reg,'search_value':search_value})

def home(request):
    print("region is NA1")
    return render(request,'main\\search.html', {'region': "NA1"})

def setRegion(request, region):
    print("set region as : " +region)
    return render(request,'main\\search.html', {'region': region})

def update(request, search_value, region ="NA1"):
    watcher = RiotWatcher('RGAPI-c9b71261-6f44-46df-8fb4-16d977e9411a')
    reg = region
    ## handle non english name
    chamList = {"1": "Annie", "2": "Olaf", "3": "Galio", "516": "Ornn", "5": "XinZhao",
                "6": "Urgot", "7": "Leblanc", "8": "Vladimir", "9": "Fiddlesticks", "10": "Kayle",
                "11": "MasterYi", "12": "Alistar", "13": "Ryze", "14": "Sion", "15": "Sivir",
                "16": "Soraka", "17": "Teemo", "18": "Tristana", "19": "Warwick", "20": "Nunu",
                "21": "MissFortune", "22": "Ashe", "23": "Tryndamere", "24": "Jax", "4": "TwistedFate",
                "26": "Zilean", "27": "Singed", "28": "Evelynn", "29": "Twitch", "30": "Karthus",
                "31": "Chogath", "32": "Amumu", "33": "Rammus", "34": "Anivia", "35": "Shaco",
                "36": "DrMundo", "37": "Sona", "38": "Kassadin", "39": "Irelia", "40": "Janna",
                "41": "Gangplank", "42": "Corki", "43": "Karma", "44": "Taric", "45": "Veigar",
                "48": "Trundle", "50": "Swain", "51": "Caitlyn", "53": "Blitzcrank", "54": "Malphite",
                "55": "Katarina", "56": "Nocturne", "57": "Maokai", "58": "Renekton", "59": "JarvanIV",
                "60": "Elise", "61": "Orianna", "62": "MonkeyKing", "63": "Brand", "64": "LeeSin",
                "67": "Vayne", "68": "Rumble", "69": "Cassiopeia", "72": "Skarner", "74": "Heimerdinger",
                "75": "Nasus", "76": "Nidalee", "77": "Udyr", "78": "Poppy", "79": "Gragas",
                "80": "Pantheon", "81": "Ezreal", "82": "Mordekaiser", "83": "Yorick", "84": "Akali",
                "85": "Kennen", "86": "Garen", "89": "Leona", "90": "Malzahar", "91": "Talon", "92": "Riven",
                "96": "KogMaw", "98": "Shen", "99": "Lux", "101": "Xerath", "102": "Shyvana",
                "103": "Ahri", "104": "Graves", "105": "Fizz", "106": "Volibear", "107": "Rengar",
                "110": "Varus", "111": "Nautilus", "112": "Viktor", "113": "Sejuani", "114": "Fiora",
                "115": "Ziggs", "117": "Lulu", "119": "Draven", "120": "Hecarim", "121": "Khazix",
                "122": "Darius", "126": "Jayce", "127": "Lissandra", "131": "Diana", "133": "Quinn",
                "134": "Syndra", "136": "AurelionSol", "141": "Kayn", "142": "Zoe", "143": "Zyra",
                "150": "Gnar", "25": "Morgana", "154": "Zac", "157": "Yasuo", "161": "Velkoz",
                "163": "Taliyah", "164": "Camille", "201": "Braum", "202": "Jhin", "203": "Kindred",
                "222": "Jinx", "223": "TahmKench", "236": "Lucian", "238": "Zed", "240": "Kled", "245": "Ekko",
                "254": "Vi", "266": "Aatrox", "267": "Nami", "268": "Azir", "412": "Thresh", "420": "Illaoi",
                "421": "RekSai", "427": "Ivern", "429": "Kalista", "432": "Bard", "497": "Rakan", "498": "Xayah"}
    type_dict = {400: 'Draft Pick',
                 420: 'Ranked Solo',
                 430: 'Blind Pick',
                 440: 'Ranked Flex',
                 450: 'ARAM',
                 460: '3v3 Blind Pick',
                 470: '3v3 Ranked Flex',
                 900: 'ARURF'}
    try:
        name = search_value.replace("%20", " ")
        print name
        #summoner info
        summoner_info = watcher.summoner.by_name(region, name)
        print('here')
        acc_id = summoner_info["accountId"]
        summoner_id = str(summoner_info['id'])
        name = summoner_info["name"]

        print("######### summoner info #########")
        print(name)
        #match info
        match_list = []
        matchlist = watcher.match.matchlist_by_account_recent(region, acc_id)

        print("##### matchlist #####")
        # print(matchlist['matches'])
        for match in matchlist['matches']:
            matchId = match['gameId']
            time = datetime.datetime.fromtimestamp(match['timestamp']/1000).strftime('%Y-%m-%d %H:%M:%S')

            try: type = type_dict[match['queue']]
            except Exception as error: type = 'Unusual'


            match_detail = watcher.match.by_id(region, matchId)

            participantId = [participant['participantId'] for participant in match_detail['participantIdentities'] if
                             participant['player']['summonerName'] == name][0]

            participant = [participant for participant in match_detail['participants'] if
                           participant['participantId'] == participantId][0]

            team_size = len(match_detail['participantIdentities'])/2


            itemkeys = ['item0', 'item1', 'item2', 'item3', 'item4', 'item5', 'item6']
            items = []
            for key in itemkeys:
                item = participant['stats'][key]

                if item==0:
                    item = 3637
                items.append(item)

            doublekill = participant['stats']['doubleKills'] > 0
            triplekill = participant['stats']['tripleKills'] > 0
            quadrakill = participant['stats']['quadraKills'] > 0
            pentakill = participant['stats']['pentaKills'] > 0
            cId = participant['championId']
            champion = chamList[str(cId)]
            duration = datetime.datetime.fromtimestamp(match_detail['gameDuration']).strftime('%M:%S')

            m = Match(
                seasonId=match_detail['seasonId'],
                queueId = match_detail['queueId'],
                gameId = match_detail['gameId'],
                participantIdentities = match_detail['participantIdentities'],
                gameVersion = match_detail['gameVersion'],
                platformId = match_detail['platformId'],
                gameMode = match_detail['gameMode'],
                mapId = match_detail['mapId'],
                gameType = match_detail['gameType'],
                teams = match_detail['teams'],
                participants = match_detail['participants'],
                gameDuration = match_detail['gameDuration'],
                gameCreation = match_detail['gameCreation'],
            )

            obj, created = Match.objects.get_or_create(gameId=match_detail['gameId'],defaults=match_detail)

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
                               'gameType': type,
                               'teamSize':team_size,
                               'time':time,
                               'duration':duration,
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
            # 0 is solo, 1 is flex
            leagues = try_league[0]
            summoner_league = leagues['tier'] + ' ' + leagues['rank']
            points = leagues['leaguePoints']
            wins = leagues['wins']
            losses = leagues['losses']
            lp = LeaguePositionDTO(
                rank=leagues['rank'],
                queueType = leagues['queueType'],
                hotStreak = leagues['hotStreak'],
                wins =leagues['wins'],
                veteran = leagues['veteran'],
                losses =leagues['losses'],
                freshBlood =leagues['freshBlood'],
                leagueId = leagues['leagueId'],
                playerOrTeamName = leagues['playerOrTeamName'],
                inactive = leagues['inactive'],
                playerOrTeamId = leagues['playerOrTeamId'],
                leagueName = leagues['leagueName'],
                tier = leagues['tier'],
                leaguePoints =leagues['leaguePoints']
            )
            obj, created = LeaguePositionDTO.objects.update_or_create(playerOrTeamName = leagues['playerOrTeamName'],playerOrTeamId = leagues['playerOrTeamId'],defaults=leagues)

        if losses == 0:
            if wins == 0: rate = 0
            else: rate = 100
        else:
            rate = round(float(wins)/float(wins+losses)*100, 2)
        print("######### league info #########")
        print(summoner_league)



        mastery_list = watcher.champion_mastery.by_summoner(region,summoner_id)
        for mast in mastery_list:
            mast['champion'] = chamList[str(mast['championId'])]
            cm = ChampionMasteryDTO(
                chestGranted=mast['chestGranted'],
                championLevel = mast['championLevel'],
                championPoints = mast['championPoints'],
                championId = mast['championId'],
                playerId = mast['playerId'],
                championPointsUntilNextLevel = mast['championPointsUntilNextLevel'],
                tokensEarned = mast['tokensEarned'],
                championPointsSinceLastLevel = mast['championPointsSinceLastLevel'],
                lastPlayTime = mast['lastPlayTime']
            )
            # obj, created = ChampionMasteryDTO.objects.update_or_create(playerId = mast['playerId'],championId = mast['championId'],defaults=mast)

        carry = random.randint(0, 100)
        teamwork = random.randint(0, 100)
        support = random.randint(0, 100)
        farm = random.randint(0, 100)
        survive = random.randint(0, 100)
        allrounder = random.randint(0, 100)
        analysis = {'carry': carry, 'teamwork': teamwork, 'support': support, 'farm': farm, 'survive': survive,
                    'allrounder': allrounder}

        summoner = summoner_info.copy()
        summoner['matchList']=matchlist
        summoner['analysis']=analysis
        s = SummonerDTO(
            profileIconId=summoner_info['profileIconId'],
            name = summoner_info['name'],
            summonerLevel = summoner_info['summonerLevel'],
            revisionDate = summoner_info['revisionDate'],
            id = summoner_info['id'],
            accountId = summoner_info['accountId'],
            matchList = matchlist,
            analysis = analysis
        )
        obj, created=SummonerDTO.objects.get_or_create(accountId=summoner_info['accountId'],id = summoner_info['id'],defaults=summoner)




    except Exception as err:
        print('This is the error')
        print(str(err))
        return render(request, "main\\search.html", {'error': True})

    return render(request, 'main\\search.html', {
                                           'region': reg,
                                           'search_value':search_value,
                                           'summoner_info': summoner_info,
                                           'name': summoner_info['name'],
                                           'icon': summoner_info['profileIconId'],
                                           'league': summoner_league,
                                           'points': points,
                                           'level': summoner_info['summonerLevel'],
                                           'wins': wins,
                                           'losses': losses,
                                           'rate': rate,
                                           'match_list': match_list,
                                           'mastery_list': mastery_list,
                                           'analysis': analysis,
                                           'error':False,
                                           'notfound':False})

def champions(request, region, league="", time=""):
    if not time:
        time = "All2"
    if not league:
        league="All"
    chamList = {"1": "Annie", "2": "Olaf", "3": "Galio", "516": "Ornn", "5": "XinZhao",
                "6": "Urgot", "7": "Leblanc", "8": "Vladimir", "9": "Fiddlesticks", "10": "Kayle",
                "11": "MasterYi", "12": "Alistar", "13": "Ryze", "14": "Sion", "15": "Sivir",
                "16": "Soraka", "17": "Teemo", "18": "Tristana", "19": "Warwick", "20": "Nunu",
                "21": "MissFortune", "22": "Ashe", "23": "Tryndamere", "24": "Jax", "4": "TwistedFate",
                "26": "Zilean", "27": "Singed", "28": "Evelynn", "29": "Twitch", "30": "Karthus",
                "31": "Chogath", "32": "Amumu", "33": "Rammus", "34": "Anivia", "35": "Shaco",
                "36": "DrMundo", "37": "Sona", "38": "Kassadin", "39": "Irelia", "40": "Janna",
                "41": "Gangplank", "42": "Corki", "43": "Karma", "44": "Taric", "45": "Veigar",
                "48": "Trundle", "50": "Swain", "51": "Caitlyn", "53": "Blitzcrank", "54": "Malphite",
                "55": "Katarina", "56": "Nocturne", "57": "Maokai", "58": "Renekton", "59": "JarvanIV",
                "60": "Elise", "61": "Orianna", "62": "MonkeyKing", "63": "Brand", "64": "LeeSin",
                "67": "Vayne", "68": "Rumble", "69": "Cassiopeia", "72": "Skarner", "74": "Heimerdinger",
                "75": "Nasus", "76": "Nidalee", "77": "Udyr", "78": "Poppy", "79": "Gragas",
                "80": "Pantheon", "81": "Ezreal", "82": "Mordekaiser", "83": "Yorick", "84": "Akali",
                "85": "Kennen", "86": "Garen", "89": "Leona", "90": "Malzahar", "91": "Talon", "92": "Riven",
                "96": "KogMaw", "98": "Shen", "99": "Lux", "101": "Xerath", "102": "Shyvana",
                "103": "Ahri", "104": "Graves", "105": "Fizz", "106": "Volibear", "107": "Rengar",
                "110": "Varus", "111": "Nautilus", "112": "Viktor", "113": "Sejuani", "114": "Fiora",
                "115": "Ziggs", "117": "Lulu", "119": "Draven", "120": "Hecarim", "121": "Khazix",
                "122": "Darius", "126": "Jayce", "127": "Lissandra", "131": "Diana", "133": "Quinn",
                "134": "Syndra", "136": "AurelionSol", "141": "Kayn", "142": "Zoe", "143": "Zyra",
                "150": "Gnar", "25": "Morgana", "154": "Zac", "157": "Yasuo", "161": "Velkoz",
                "163": "Taliyah", "164": "Camille", "201": "Braum", "202": "Jhin", "203": "Kindred",
                "222": "Jinx", "223": "TahmKench", "236": "Lucian", "238": "Zed", "240": "Kled", "245": "Ekko",
                "254": "Vi", "266": "Aatrox", "267": "Nami", "268": "Azir", "412": "Thresh", "420": "Illaoi",
                "421": "RekSai", "427": "Ivern", "429": "Kalista", "432": "Bard", "497": "Rakan", "498": "Xayah"}
    cham_list = []
    for key in chamList:
        champion = chamList[key]
        played= random.randint(50000, 100000)
        rate = round(float(random.randint(1, played))/float(played),2)
        kills= random.randint(0,100)
        deaths= random.randint(0,100)
        assists= random.randint(0,100)
        if deaths == 0:
            kda = "Perfect"
        else:
            kda = round(float(kills+assists)/float(deaths),2)
        gold = random.randint(5000,20000)
        cham_list.append({'champion':champion,'played':played,'rate':rate,'kda':kda,'gold':gold})
    return render(request, 'main\\champions.html',{'cham_list':cham_list, 'region': region, 'league':league,'time':time})