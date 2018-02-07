from riotwatcher import RiotWatcher

def crawl_data(account_id,name):
    watcher = RiotWatcher('RGAPI-037a581d-1a62-4dc6-9040-f6de10e853bf')
    my_region = 'jp1'

    # if account_id is not None:
    #     client = MongoClient()
    #     db = client.test
    #     try:
    #         response = watcher.summoner.by_account(my_region, account_id)
    #         print(response)
    #         db.test.insert_one(response)
    #     except Exception as err:
    #         print(err)
    if name is not None:
        #client = MongoClient()
        #db = client.test
        try:
            summoner_info = watcher.summoner.by_name(my_region, name)
            print("############# Summoner Info #############")
            print(summoner_info is None)

            acc_id = summoner_info["accountId"]
            #print(acc_id)
            #print(summoner_info['id'])
            matchlist = watcher.match.matchlist_by_account_recent(my_region,acc_id)
            print(matchlist is None)
            for match in matchlist['matches']:
                matchId = match['gameId']
                match_detail = watcher.match.by_id(my_region, matchId)
                match.update({'detail': match_detail})
            summoner_id = str(summoner_info['id'])
            print(summoner_id is None)
            try_league = watcher.league.positions_by_summoner(my_region, summoner_id)

            league = {'league':'Unranked', 'points':0, 'wins':0, 'losses':0}
            if (try_league != []):
                leagues = try_league[0]
                summoner_league = leagues['tier']+' '+leagues['rank']
                points = leagues['leaguePoints']
                wins = leagues['wins']
                losses = leagues['losses']
                league = {'league':summoner_league,'points':points,'wins':wins,'losses':losses}
            summoner_info.update({'matchlist': matchlist, 'league': league})
            print(summoner_info is None)
            # db.test.insert_one(summoner_info)
            return summoner_info
        except Exception as err:
            print(err)

def search_by_name(name):
    #client = MongoClient()
    #db = client.test
    # cursor = db.test.find({'name': name})
    # for document in cursor:
    #     return document
    # if not cursor.count():
    return crawl_data(None, name)
