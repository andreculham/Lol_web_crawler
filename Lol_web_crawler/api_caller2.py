from riotwatcher import RiotWatcher
import time
import json
watcher = RiotWatcher('RGAPI-b17a8469-7cf1-4f9d-bbd7-e244a4225b92')

my_region = 'jp1'
'''
me = watcher.summoner.by_name(my_region, 'test')
print(me)

# all objects are returned (by default) as a dict
# get my 1 mastery page i keep changing
my_mastery_pages = watcher.masteries.by_summoner(my_region, me['id'])
print(my_mastery_pages)

# lets see if i got diamond yet (i probably didnt)
my_ranked_stats = watcher.league.leagues_by_summoner(my_region, me['id'])
print(my_ranked_stats)

# Lets some champions
static_champ_list = watcher.static_data.champions(my_region)
print(static_champ_list)

# Error checking requires importing HTTPError from requests
'''
from requests import HTTPError

# For Riot's API, the 404 status code indicates that the requested data wasn't found and
# should be expected to occur in normal operation, as in the case of a an
# invalid summoner name, match ID, etc.
#
# The 429 status code indicates that the user has sent too many requests
# in a given amount of time ("rate limiting").

start_time = time.time()
data = {}  
data['matches'] = []
i=1
while 1:
    try:
        response = watcher.match.by_id(my_region, i+99)
        print(response)
        data['summoner'].append(response)
        with open('match.json' , 'w', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False))
    except HTTPError as err:
        if err.response.status_code == 403:
            print('API Key is invalid or has expired')
            break
        else:
            print(err)
        '''
    #for rate limit being 100 request per 2 minutes
    if i % 100 == 0:
        time_now = time.time()
        time.sleep(120 -(time_now - start_time))
        start_time = time_now
    # for rate limit being 20 request per second
    '''
    i += 1
    

