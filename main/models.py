from django.db import models
from django.contrib.postgres.fields import JSONField
import time

class Match(models.Model):
    seasonId = models.IntegerField()
    queueId = models.IntegerField()
    gameId = models.BigIntegerField()
    participantIdentities = JSONField()
    gameVersion = models.CharField(max_length=200)
    platformId = models.CharField(max_length=200)
    gameMode = models.CharField(max_length=200)
    mapId = models.IntegerField()
    gameType = models.CharField(max_length=200)
    teams = JSONField()
    participants = JSONField()
    gameDuration = models.BigIntegerField()
    gameCreation = models.BigIntegerField()


class SummonerDTO(models.Model):
    profileIconId = models.IntegerField()
    name = models.CharField(max_length=200)
    summonerLevel = models.BigIntegerField()
    revisionDate = models.BigIntegerField()
    id = models.BigIntegerField()
    accountId = models.BigIntegerField(primary_key=True)


class ChampionMasteryDTO(models.Model):
    chestGranted = models.BooleanField()
    championLevel = models.IntegerField()
    championPoints = models.IntegerField()
    championId = models.BigIntegerField()
    playerId = models.BigIntegerField()
    championPointsUntilNextLevel = models.BigIntegerField()
    tokensEarned = models.IntegerField()
    championPointsSinceLastLevel = models.BigIntegerField()
    lastPlayTime = models.BigIntegerField()

class ChampionDto(models.Model):
    rankedPlayEnabled = models.BooleanField()
    botEnabled = models.BooleanField()
    botMmEnabled = models.BooleanField()
    active = models.BooleanField()
    freeToPlay = models.BooleanField()
    id = models.BigIntegerField(primary_key=True)



    
