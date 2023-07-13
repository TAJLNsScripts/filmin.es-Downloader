import requests
import cookies
import json
import base64
import subprocess
import os
from pywidevine.cdm import Cdm
from pywidevine.device import Device
from pywidevine.pssh import PSSH
from bs4 import BeautifulSoup

cookies = cookies.cookies

#Config
MyWVD = "./WVD.wvd"

def ascii_clear():
    os.system('cls||clear')
    print("""                                                                                              
  
    JP555555555PJ 7P55555P   P55555PJ      P555555P5.  ^P55555555   7777777   777777!.  ^7777777   
    YPPPPPPPPPPPJ ?PPPPPPP   PPPPPPPJ      PPPPPPPPP~  ?PPPPPPPPP   7777777   7777777~  ^7777777    
    JPPPPPPPPPPPJ ?PPPPPPP   PPPPPPPJ      PPPPPPPPP? .YPPPPPPPPP   7777777   77777777: ^7777777    
    JPPPPPPPP     ?PPPPPPP   PPPPPPPJ      PPPPPPPPPY ^PPPPPPPPPP   7777777   777777777.^7777777    
    JPPPPPPPP     ?PPPPPPP   PPPPPPPJ      PPPPPPPPPP:!PPPPPPPPPP   7777777   777777777!~7777777    
    JPPPPPPPPPPP7 ?PPPPPPP   PPPPPPPJ      PPPPPP55PP?YPP55PPPPPP   7777777   777777777777777777    
    JPPPPPPPPPPP7 ?PPPPPPP   PPPPPPPJ      PPPPPPJ7PPPPP5!5PPPPPP   7777777   777777777777777777    
    JPPPPPPP^     ?PPPPPPP   PPPPPPPJ      PPPPPP?:5PPPPY.5PPPPPP   7777777   7777777^7777777777    
    JPPPPPPP^     ?PPPPPPP   PPPPPPPJ      PPPPPPJ JPPPP!.5PPPPPP   7777777   7777777.:777777777    
    JPPPPPPP^     ?PPPPPPP   PPPPPPPYPPPP  PPPPPPJ ~PPP5:.5PPPPPP   7777777   7777777: ~77777777    
    YPPPPPPP^     ?PPPPPPP   PPPPPPPPPPPP  PPPPPPJ .5PPJ .5PPPPPP   7777777   7777777: .77777777    
    JPPPPPPP^     7PPPPPPP   PPPPPPPPPPPP  PPPPPP?  ?PP~ .5PPPPP5   7777777   7777777.  :777777!    
   
                                        Downloader                                      
                                        TAJLN 2023                                      
""")

def do_cdm(manifest_url, license_url, series_name, season_name, episode_name):
    fkeys = ""

    manifest = requests.get(manifest_url)
    
    if manifest.status_code != 200:
        print(title)
        print('    Invalid manifest found')
        return
    
    pssh = PSSH(BeautifulSoup(manifest.content, 'html.parser').findAll('cenc:pssh')[0].text)

    #CDM processing

    device = Device.load(MyWVD)
    cdm = Cdm.from_device(device)
    session_id = cdm.open()
    challenge = cdm.get_license_challenge(session_id, pssh)

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    licence = requests.post(license_url, headers=headers, data=challenge)
    licence.raise_for_status()
    cdm.parse_license(session_id, licence.content)

    for key in cdm.get_keys(session_id):
        if key.type != 'SIGNING':
            fkeys += key.kid.hex + ":" + key.key.hex()
            
    cdm.close(session_id)

    print("    MPD: " + manifest_url)
    print("    Key: " + fkeys)
    
    print('    Downloading')
    subprocess.run(['N_m3u8DL-RE.exe', '--save-dir', 'Downloads/' + season_name, '--key', fkeys, '--save-name', episode_name, '-sv', 'best',  '-sa', 'best', manifest_url, '-M', 'mp4'])
    

def request_url(url):

    name = url.rsplit('/', 1)[-1]

    headers = {
        'x-requested-with': 'XMLHttpRequest',
    }

    response = requests.get('https://www.filmin.es/wapi/medias/serie/' + name, cookies=cookies, headers=headers)
    
    try:
        data = json.loads(response.content)['data']
        
        r = {}
        r['series_id'] = str(data['id'])
        r['series_name'] = data['title']
        
        return r
    except:
        print('Error getting id')
        print(response)
        quit()

def get_seasons(series_id):
    headers = {
        'x-client-id': 'GqykKp6LzeGZCPs7',
        'x-client-version': '5ecad915aecb247c828a11c9b2e35694a6df99b4',
        'x-device-model': 'See User Agent',
        'x-device-os-version': 'See User Agent',
    }

    response = requests.get('https://uapi.filmin.es/medias/' + series_id + '/seasons', headers=headers)
    
    try:
        data = json.loads(response.content)['data']
        seasons = data['seasons']
        return seasons
    except:
        print('Error getting seasons')
        print(response)
        quit()

def get_episodes(series_id, season_id):
    headers = {
        'x-client-id': 'GqykKp6LzeGZCPs7',
        'x-client-version': '5ecad915aecb247c828a11c9b2e35694a6df99b4',
        'x-device-model': 'See User Agent',
        'x-device-os-version': 'See User Agent',
    }

    response = requests.get('https://uapi.filmin.es/medias/' + series_id + '/seasons/' + season_id + '/episodes', headers=headers)
    
    try:
        data = json.loads(response.content)['data']
        episodes = data['episodes']
        return episodes
    except:
        print('Error getting episodes')
        print(response)
        quit()

def do_episode(episode_id, series_name, season_name):

    #Stage 1
    headers = {
        'x-requested-with': 'XMLHttpRequest',
    }

    response = requests.get('https://www.filmin.es/player/data/episode/' + episode_id, cookies=cookies, headers=headers)
    
    try:
        media = json.loads(response.content)['media']
        episode_name = str(media['episode']) + '. ' + media['title']
        version = str(media['versions'][0]['id'])
    except:
        print('Error getting episode version')
        print(response)
        quit()
    
    #Stage 2
    response = requests.get('https://www.filmin.es/player/data/episode/' + episode_id + '/' + version, cookies=cookies, headers=headers)
    
    try:
        sources = json.loads(response.content)['sources']
        
        for s in sources:
            if s['profile'] == 'dash+https+widevine':
                manifest_url = s['file']
                licence_url = s['license']
                break;
                
    except:
        print('Error getting episode sources')
        print(response)
        quit()
    
    do_cdm(manifest_url, licence_url, series_name, season_name, episode_name)

#https://www.filmin.es/wapi/medias/serie/castigo

ascii_clear()
url = input('Enter series url: ')

url_request = request_url(url)
series_id = url_request['series_id']
series_name = url_request['series_name']

seasons = get_seasons(series_id)

#Season picker
print('Found ' + str(len(seasons)) +  ' seasons:')

i = 1
for s in seasons:
    print(str(i) + '. ' + s['_type'] + ' ' + str(s['season_number']))
    i+=1

choice = int(input('\nChoose season: '))
season_id = str(seasons[choice-1]['id'])
season_name = 'Season ' + str(seasons[choice-1]['season_number'])

#Episode picker
episodes = get_episodes(series_id, season_id)

ascii_clear()
print('Found ' + str(len(seasons)) +  ' episodes in ' + season_name + ':')

i = 1
for e in episodes:
    print(str(i) + '. S' + str(e['season_number']) + 'E' + str(e['episode_number']) + ' ' + e['title'])
    i+=1

print("\nTo choose more then 1, follow format example: 1-x")
choice = input('Choose episode: ')

if '-' in choice:
    choice = choice.split('-')
    n1 = int(choice[0])
    n2 = int(choice[1])
    
    if(n1 < 1 or n2 > len(episodes)):
        n1 = 1
    
    if(n2 > len(episodes)):
        n2 = len(episodes)
    
    for i in range(n1, n2+1):
        do_episode(str(episodes[i-1]['id']), series_name, season_name)
else:
    do_episode(str(episodes[int(choice)-1]['id']), series_name, season_name)
