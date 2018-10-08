from django.http import HttpResponse
from django.shortcuts import render
from .models import Tweet

from twitter import *
from janome.tokenizer import Tokenizer
import requests
import json
import datetime,pytz
import urllib
import calendar
import re

BASEURL = "http://hackathon.mssf.jp/socialize5_1/"
CID = 2018101102
LID = 'pw02'

CONSUMER_KEY        = 'Yv0bhw3UuaqQudLRvjkJedi2d'
CONSUMER_SECRET_KEY = 'vwu8z3uNxNh0xCpvR8UmmBVE3wn5uvRRwDGoFxJdk2NXSnb3wa'
ACCESS_TOKEN        = '219330389-KTcnHtvS1XNOyvSLVadDSK8uM7H0AuRZxh01bOFv'
ACCESS_TOKEN_SECRET = 'lrrQNjsWA3XmeU6xN9DzFQfFBAarTEekhgiTK2KBdpFGS'

def main(request):
    return HttpResponse("Hello!")

def input(request):
    name = request.GET.get("name")
    if name == None:
        tweets = Tweet.objects.all()
    else:
        tweets = Tweet.objects.filter(screen_name=name)
    for tweet in tweets:
        text = re.sub('(https?|ftp)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+)', ' ', tweet.text)
        events = ['screen_name_' + tweet.screen_name]
        events.extend(janome(text))
        events.extend(hashTag(text))
        created_at = tweet.created_at.strftime('%Y/%m/%d %H:%M:%S')
        print(events)
        r = setEvent(created_at, events)
    return HttpResponse(r)

def crawl(request):
    name = request.GET.get("name")
    if name == None:
        name = "gaiaxnews"
    tweets = importTweet(name)
    for tweet in tweets:
        if Tweet.objects.filter(status_id=tweet['id']).count() ==0:
            creation = Tweet(status_id=tweet['id'], screen_name=tweet['screen_name'],text=tweet['text'],created_at=tweet['created_at']);
            creation.save()
    return HttpResponse("Crawled!")
 
def status(request):
    apiurl = BASEURL + "build/getstatus"
    
    query = {
        'clientid': CID,
        'libraryid': LID, 
    }
    r = requests.post(apiurl, params=query)

    return HttpResponse(r)

def stop(request):
    apiurl = BASEURL + "extract/stop"
    requestid = request.GET.get("requestid")
    query = {
        'clientid': CID,
        'requestid': requestid, 
    }
    r = requests.post(apiurl, params=query)

    return HttpResponse(r)

def drop(request):
    apiurl = BASEURL + "manage/removelibrary"
    
    query = {
        'clientid': CID,
        'libraryid': LID, 
    }
    r = requests.post(apiurl, params=query)

    return HttpResponse(r)

def extract(request):
    word = request.GET.get("word")
    if word == None:
        word = "ガイアックス"
    apiurl = BASEURL + "extract/execute"

    basenode=urllib.parse.quote(word) 
    query = {
        'clientid': CID,
        'libraryid': LID,
        'basenode': basenode,
        'preset': '1_5',
        'precision': 5,
        'decay': True,
    }
    r = requests.post(apiurl, params=query)
    dec = r.json()
    requestid = dec['requestid']
    print('request id: ' + str(requestid))

    apiurl = BASEURL + "extract/getresult"
    query = {
        'clientid': CID,
        'requestid': requestid,
    }
    r = requests.post(apiurl, params=query)
    datas={}
    node_list={}
    for node_name, distance in r.json()['basenodeDistance']['values'].items():
        datas[urllib.parse.unquote(node_name)]=distance
        #node_list.append({'name':urllib.parse.unquote(node_name), 'distance':distance})
        #print(node_name + " : " + str(distance))
    for k, v in sorted(datas.items(), key=lambda x: x[1]):
        node_list[k]=v

    for node_name,similarity  in r.json()['nodeSimilarity']['values'].items():
        name = urllib.parse.unquote(node_name)
        #print(name + " : " + str(similarity))
    return render(request, 'practice/index.html', {'node_list': node_list })

def setEvent(date_time, events):
    event_data = ""
    for event in events:
        event_data += "," + urllib.parse.quote(event)

    apiurl = BASEURL + "build/execute/event"
    query = {
        'clientid': CID,
        'libraryid': LID, 
        'event': date_time + event_data
    }
    #print(query)
    return requests.post(apiurl, params=query)


def importTweet(screen_name):
    t = Twitter(auth=OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET_KEY))
  
    timelines = t.statuses.user_timeline(screen_name=screen_name, exclude_replies="true", tweet_mode="extended", count=200)
    tweets = []
    for timeline in timelines:
        id = timeline['id']
        tweets.append({'id':timeline['id'], 'created_at':YmdHMS(timeline['created_at']), 'screen_name':timeline['user']['screen_name'], 'text':timeline['full_text']})
    return tweets

def YmdHMS(created_at):
    jst = pytz.timezone('Japan')
    utc = datetime.datetime.strptime(created_at, '%a %b %d %H:%M:%S +0000 %Y')
    return utc.replace(tzinfo=jst)

def janome(text):
    t = Tokenizer()
    tokens = t.tokenize(text)
    data = []
    for token in tokens:
        partOfSpeech = token.part_of_speech.split(',')[0]
        if partOfSpeech == u'名詞':
            if token.surface != "#":
                data.append(token.surface)
    return data

def hashTag(text):
    pattern = '[#＃]([\w一-龠ぁ-んァ-ヴーａ-ｚ]+)'
    hashTags = re.findall(pattern, text)
    return hashTags
