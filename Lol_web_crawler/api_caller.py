from riotwatcher import RiotWatcher


watcher = RiotWatcher('RGAPI-85a0a75d-7685-4cf4-9494-71673a0880ee')

my_region = 'na1'
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

nameList = ['test','test1','test2','test3']
for summoner_name in nameList:
    try:
        response = watcher.summoner.by_name(my_region, summoner_name)
    except Exception as err:
        print(err)
