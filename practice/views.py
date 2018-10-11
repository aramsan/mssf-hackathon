from django.http import HttpResponse
from django.shortcuts import render
from .models import Tweet

from twitter import *
from janome.tokenizer import Tokenizer
import requests
import json
import time,datetime,pytz
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
    return render(request, 'practice/index.html')

def input(request):
    name = request.GET.get("name")
    inputRelation(name)
    return HttpResponse('完了')

def inputRelation(name):
    if name == None:
        tweets = Tweet.objects.all().order_by('created_at')
    else:
        tweets = Tweet.objects.filter(screen_name=name).order_by('created_at')
    for tweet in tweets:
        text = re.sub('(https?|ftp)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+)', ' ', tweet.text)
        events = ['screen_name_' + tweet.screen_name]
        #events.extend(janome(text))
        events.extend(hashTag(text))
        created_at = tweet.created_at.strftime('%Y/%m/%d %H:%M:%S')
        #print(created_at)
        if len(events) > 1:
            print(events)
            r = setEvent(created_at, events)
    return

def link(request): 
    return render(request, 'practice/link.html')

def crawl(request):
    name = request.GET.get("name")
    if name == None:
        name = "gaiaxnews"
    crawlTweet(name)
    return HttpResponse("Crawled!")

def crawlTweet(name):
    tweets = importTweet(name)
    for tweet in tweets:
        if Tweet.objects.filter(status_id=tweet['id']).count() ==0:
            creation = Tweet(status_id=tweet['id'], screen_name=tweet['screen_name'], user_id=tweet['user_id'], user_name=tweet['user_name'], text=tweet['text'],created_at=tweet['created_at']);
            creation.save()
    return
 
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
    if request.POST.get("word"):
        screen_name = request.POST.get("twitter")
        word = request.POST.get("word")
    else:
        screen_name = request.GET.get("twitter")
        word = request.GET.get("word")
    if word == None:
        word = "screen_name_gaiaxnews"
    if screen_name == None:
        screen_name = "gaiaxnews"

    # tweet取り込んでないアカウントだったら取り込み＆関係性追加
    if Tweet.objects.filter(screen_name=screen_name).count() == 0:
        crawlTweet(screen_name)
        inputRelation(screen_name)     
        time.sleep(1)

    word_list   = executeExtract(basenode=urllib.parse.quote(word))
    print(word_list)
    if word_list[0]['error'].startswith('request'):
        return HttpResponse(word_list[0]['error'])
    if word_list[0]['screen_name']  == "":
        return HttpResponse("ご指定のワードで関係性を抽出できませんでした")
     
    account_list = executeExtract(basenode=urllib.parse.quote("screen_name_" + screen_name))
    screen_name = word_list[0]['screen_name']
    user_id = word_list[0]['user_id']
    user_name = word_list[0]['user_name'] 
    message = word + "でコラボするなら" + user_name + "さんとコラボするとおもしろいいと思います。"
 
    print(account_list)
    if account_list[0]['error'] == "" and len(account_list) >1:
        message += "もう一つ言うと、" + word + "にこだわらず" + account_list[1]['user_name'] + "さんとコラボしても面白いと思いますよ"
        if word_list[0]['distance'] > account_list[1]['distance']:
            screen_name = account_list[1]['screen_name']
            user_id = account_list[1]['user_id']
            user_name = account_list[1]['user_name']
            message = word + "でコラボするより" + user_name + "さんとコラボすることをおすすめします"

    return render(request, 'practice/result.html', {'screen_name':screen_name, 'user_id':user_id, 'user_name':user_name, 'message':message})

def executeExtract(basenode):
    apiurl = BASEURL + "extract/execute"
    query = {
        'clientid': CID,
        'libraryid': LID,
        'basenode': basenode,
        'preset': '1',
        'precision': 5,
        'decay': True,
    }
    r = requests.post(apiurl, params=query)
    dec = r.json()
    if 'requestid' not in r.json():
        return [{'error':"request idがありません。指定されたワードで関係性を抽出できませんでした", 'screen_name':""}] 
    requestid = dec['requestid']
    print('request id: ' + str(requestid))

    time.sleep(1)    
    apiurl = BASEURL + "extract/getresult"
    query = {
        'clientid': CID,
        'requestid': requestid,
    }
    r = requests.post(apiurl, params=query)
    datas={}
    node_list={}
    print(r.json()['result'])
    if r.json()['result'] == False:
        return HttpResponse(r.json()['message'])

    for node_name, distance in r.json()['basenodeDistance']['values'].items():
        datas[urllib.parse.unquote(node_name)]=distance
        #node_list.append({'name':urllib.parse.unquote(node_name), 'distance':distance})
        #print(node_name + " : " + str(distance))
    match_list = []
    for k, v in sorted(datas.items(), key=lambda x: x[1]):
        node_list[k]=v
        #print(basenode + ": " + str(k)+ " : " + str(v))
        if k.startswith("screen_name_"):
            screen_name = k.replace("screen_name_","")
            data = Tweet.objects.filter(screen_name=screen_name)
            match_list.append({'screen_name':screen_name, 'user_id':data[0].user_id, 'user_name':data[0].user_name, 'distance':v, 'error':''})

    return match_list




def evaluategraph(request): 
    apiurl = BASEURL + "manage/evaluategraph"
    query = {
        'clientid': CID,
        'libraryid': LID, 
    }
    r = requests.post(apiurl, params=query)
    return HttpResponse(r)

def getnodelist(request):
    apiurl = BASEURL + "manage/getnodelist"
    query = {
        'clientid': CID,
        'libraryid': LID, 
    }
    r = requests.post(apiurl, params=query)
    node_list = []
    for node_name in r.json()['nodes']:
         node_list.append(urllib.parse.unquote(node_name))
    return render(request, 'practice/getnodelist.html', {'node_list': node_list })

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
    return requests.post(apiurl, params=query)


def importTweet(screen_name):
    t = Twitter(auth=OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET_KEY))
  
    timelines = t.statuses.user_timeline(screen_name=screen_name, exclude_replies="true", tweet_mode="extended", count=200)
    tweets = []
    for timeline in timelines:
        id = timeline['id']
        tweets.append({'id':timeline['id'], 'created_at':YmdHMS(timeline['created_at']), 'screen_name':timeline['user']['screen_name'], 'user_id':timeline['user']['id'], 'user_name':timeline['user']['name'], 'text':timeline['full_text']})
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
    extends = []
    for hashTag in hashTags:
        words = janome(hashTag)
        for word in words:
            if word != hashTag:
                extends.append(word)
    hashTags.extend(extends)
    return hashTags
