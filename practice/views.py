from django.http import HttpResponse
from django.shortcuts import render
import requests
import json
import time
import urllib

BASEURL = "http://hackathon.mssf.jp/socialize5_1/"
CID = 2018101102
LID = 'pw02'

def main(request):
    return HttpResponse("Hello!")

def input(request):
    apiurl = BASEURL + "build/execute/event"
    
    query = {
        'clientid': CID,
        'libraryid': LID, 
        'event': '2018/10/01 10:00:00,japan,' + urllib.parse.quote('アメリカ')
    }
    print(query)
    r = requests.post(apiurl, params=query)

    query = {
        'clientid': CID,
        'libraryid': LID, 
        'event': '2018/10/02 10:00:00,korea,german,japan'
    }
    r = requests.post(apiurl, params=query)

    return HttpResponse(r)
    
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
    apiurl = BASEURL + "extract/execute"
    
    query = {
        'clientid': CID,
        'libraryid': LID,
        'basenode': 'japan',
        'preset': '1',
    }
    r = requests.post(apiurl, params=query)
    dec = r.json()
    requestid = dec['requestid']

    apiurl = BASEURL + "extract/getresult"
    query = {
        'clientid': CID,
        'requestid': requestid,
    }
    r = requests.post(apiurl, params=query)
    node_list={}
    for node_name, distance in r.json()['basenodeDistance']['values'].items():
        name = urllib.parse.unquote(node_name)
        print(name)
        node_list[name] = distance

    return render(request, 'practice/index.html', {'node_list': node_list })

