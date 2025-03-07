# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Canale per Mediaset Play
# ------------------------------------------------------------
from platformcode import logger
import uuid

import requests, sys
from core import support
if sys.version_info[0] >= 3: from urllib.parse import urlencode, quote
else: from urllib import urlencode, quote
if sys.version_info[0] >= 3: from concurrent import futures
else: from concurrent_py2 import futures
from collections import OrderedDict

PAGINATION = 4

host = ''
post_url = '?assetTypes=HD,browser,widevine,geoIT|geoNo:HD,browser,geoIT|geoNo:HD,geoIT|geoNo:SD,browser,widevine,geoIT|geoNo:SD,browser,geoIT|geoNo:SD,geoIT|geoNo&auto=true&balance=true&format=smil&formats=MPEG-DASH,MPEG4,M3U&tracking=true'
deviceid = '61d27df7-5cbf-4419-ba06-cfd27ecd4588'
loginUrl = 'https://api-ott-prod-fe.mediaset.net/PROD/play/idm/anonymous/login/v1.0'
loginData = {"cid": deviceid, "platform": "pc", "appName": "web/mediasetplay-web/d667681"}
lic_url = 'https://widevine.entitlement.theplatform.eu/wv/web/ModularDrm/getRawWidevineLicense?releasePid=%s&account=http://access.auth.theplatform.com/data/Account/2702976343&schema=1.0&token={token}|Accept=*/*&Content-Type=&User-Agent=' + support.httptools.get_user_agent() + '|R{{SSM}}|'
entry = 'https://api.one.accedo.tv/content/entry/{id}?locale=it'
entries = 'https://api.one.accedo.tv/content/entries?id={id}&locale=it'
sessionUrl = "https://api.one.accedo.tv/session?appKey=59ad346f1de1c4000dfd09c5&uuid={uuid}&gid=default"

current_session = requests.Session()
current_session.headers.update({'Content-Type': 'application/json', 'User-Agent': support.httptools.get_user_agent(), 'Referer': support.config.get_channel_url()})

# login anonimo
res = current_session.post(loginUrl, json=loginData, verify=False)
Token = res.headers['t-cts']
current_session.headers.update({'t-apigw': res.headers['t-apigw'], 't-cts': Token})
lic_url = lic_url.format(token=Token)
tracecid = res.json()['response']['traceCid']
cwid = res.json()['response']['cwId']

# sessione
res = current_session.get(sessionUrl.format(uuid=str(uuid.uuid4())), verify=False)
current_session.headers.update({'x-session': res.json()['sessionKey']})

cdict = {'CWFILMTOPVIEWED':'filmPiuVisti24H',
         'CWFILMCOMEDY':'filmCommedia',
         'CWFILMACTION':'filmAzioneThrillerAvventura',
         'CWFILMDRAMATIC':'filmDrammatico',
         'CWFILMSENTIMENTAL':'filmSentimentale',
         'CWFILMCLASSIC':'filmClassici',
         'personToContentFilm':'personToContentFilm',
         'CWHOMEFICTIONNOWELITE':'stagioniFictionSerieTvSezione',
         'CWFICTIONSOAP':'mostRecentSoapOpera',
         'CWFICTIONDRAMATIC':'stagioniFictionDrammatico',
         'CWFICTIONPOLICE':'stagioniFictionPoliziesco',
         'CWFICTIONCOMEDY':'stagioniFictionCommedia',
         'CWFICTIONSITCOM':'stagioniFictionSitCom',
         'CWFICTIONSENTIMENTAL':'stagioniFictionSentimentale',
         'CWFICTIONBIOGRAPHICAL':'stagioniFictionBiografico',
         'CWPROGTVPRIME':'stagioniPrimaSerata',
         'CWPROGTVDAY':'stagioniDaytime',
         'CWPROGTVTOPVIEWED':'programmiTvClip24H',
         'CWPROGTVTALENT':'stagioniReality',
         'CWPROGTVVARIETY':'stagioniVarieta',
         'CWPROGTVTALK':'stagioniTalk',
         'CWPROGTVTG':'mostRecentTg',
         'CWPROGTVSPORT':'mostRecentSport',
         'CWPROGTVMAGAZINE':'stagioniCucinaLifestyle',
         'CWDOCUMOSTRECENT':'mostRecentDocumentariFep',
         'CWDOCUTOPVIEWED':'stagioniDocumentari',
         'CWDOCUSPAZIO':'documentariSpazio',
         'CWDOCUNATURANIMALI':'documentariNatura',
         'CWDOCUSCIENZATECH':'documentariScienza',
         'CWDOCUBIOSTORIE':'documentariBioStoria',
         'CWDOCUINCHIESTE':'documentariInchiesta',
         'CWFILMDOCU':'filmDocumentario',
         'CWKIDSBOINGFORYOU':'kidsBoing',
         'CWKIDSCARTOONITO':'kidsCartoonito',
         'CWKIDSMEDIASETBRAND':'kidsMediaset',
         'CWENABLERKIDS':'stagioniKids'}


@support.menu
def mainlist(item):
    top =  [('Dirette {bold}', ['https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-stations?sort=ShortTitle', 'live'])]

    menu = [('Film {bullet bold}', ['5acfcbc423eec6000d64a6bb', 'menu', ['Tutti','all','searchMovie']]),
            ('Fiction / Serie TV {bullet bold}', ['5acfcb3c23eec6000d64a6a4', 'menu', ['Tutte','all','searchStagioni'], 'tvshow']),
            ('Programmi TV{ bullet bold}', ['5acfc8011de1c4000b6ec953', 'menu', ['Tutti','all','searchStagioni'], 'tvshow']),
            ('Documentari {bullet bold}', ['5bfd17c423eec6001aec49f9', 'menu', ['Tutti','all',''], 'undefined']),
            ('Kids {bullet bold}', ['5acfcb8323eec6000d64a6b3', 'menu',['Tutti','all',''], 'undefined']),
            ('Family {bullet bold}', ['5e662d01a0e845001d56875b', 'menu',['Tutti','all',''], 'undefined']),
           ]

    search = ''
    return locals()


def search(item, text):
    itemlist = []
    logger.debug(text)
    item.search = text

    try:
        itemlist = peliculas(item)
    except:
        import sys
        for line in sys.exc_info():
            support.logger.error("%s" % line)

    return itemlist


def menu(item):
    logger.debug()
    itemlist = []
    if item.url:
        json = get_from_id(item)
        for it in json:
            if 'uxReference' in it: itemlist.append(
                item.clone(title=support.typo(it['title'], 'bullet bold'), url= it['landingUrl'], ref=it['uxReference'], args='', action='peliculas'))
    return itemlist


def liveDict():
    livedict = OrderedDict({})
    json = current_session.get('https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-stations?sort=ShortTitle').json()['entries']
    for it in json:
        urls = []
        if it.get('tuningInstruction') and not it.get('mediasetstation$digitalOnly'):
            guide=current_session.get('https://static3.mediasetplay.mediaset.it/apigw/nownext/' + it['callSign'] + '.json').json()['response']
            for key in it['tuningInstruction']['urn:theplatform:tv:location:any']:
                urls += key['publicUrls']
            title = it['title']
            livedict[title] = {}
            livedict[title]['urls'] = urls
            livedict[title]['plot'] = support.typo(guide['currentListing']['mediasetlisting$epgTitle'],'bold') + '\n' + guide['currentListing']['mediasetlisting$shortDescription'] + '\n' + guide['currentListing']['description'] + '\n\n' + support.typo('A Seguire:' + guide['nextListing']['mediasetlisting$epgTitle'], 'bold')
    return livedict


def live(item):
    logger.debug()
    itemlist = []
    for key, value in liveDict().items():
        itemlist.append(item.clone(title=support.typo(key, 'bold'),
                                   fulltitle=key,
                                   show=key,
                                   contentTitle=key,
                                   forcethumb=True,
                                   urls=value['urls'],
                                   plot=value['plot'],
                                   action='play',
                                   no_return=True))
    return support.thumb(itemlist, live=True)


def peliculas(item):
    logger.debug()
    itemlist = []
    titlelist = []
    contentType = ''
    if item.text:
        json = []
        itlist = []
        with futures.ThreadPoolExecutor() as executor:
            for arg in ['searchMovie', 'searchStagioni', 'searchClip']:
                item.args = ['', 'search', arg]
                itlist += [executor.submit(get_programs, item)]
            for res in futures.as_completed(itlist):
                json += res.result()
    else:
        json = get_programs(item)
    for it in json:
        if item.search.lower() in it['title'].lower() and it['title'] not in titlelist:
            titlelist.append(it['title'])
            if 'media' in it:
                action = 'findvideos'
                contentType = 'movie'
                urls = []
                for key in it['media']:
                    urls.append(key['publicUrl'])

            else:
                action = 'epmenu'
                contentType = 'tvshow'
                urls = it['mediasetprogram$brandId']
            if urls:
                title = it['mediasetprogram$brandTitle'] + ' - ' if 'mediasetprogram$brandTitle' in it and it['mediasetprogram$brandTitle'] != it['title'] else ''
                itemlist.append(
                    item.clone(channel=item.channel,
                               action=action,
                               title=support.typo(title + it['title'], 'bold'),
                               fulltitle=it['title'],
                               show=it['title'],
                               contentType=contentType if contentType else item.contentType,
                               contentTitle=it['title'] if 'movie' in [contentType, item.contentType] else '',
                               contentSerieName=it['title'] if 'tvshow' in [contentType, item.contentType] else '',
                               thumbnail=it['thumbnails']['image_vertical-264x396']['url'] if 'image_vertical-264x396' in it['thumbnails'] else '',
                               fanart=it['thumbnails']['image_keyframe_poster-1280x720']['url'] if 'image_keyframe_poster-1280x720' in it['thumbnails'] else '',
                               plot=it['longDescription'] if 'longDescription' in it else it['description'] if 'description' in it else '',
                               urls=urls,
                               seriesid = it.get('seriesId',''),
                               url=it['mediasetprogram$pageUrl'],
                               forcethumb=True,
                               no_return=True))
    return itemlist


def epmenu(item):
    logger.debug()
    itemlist = []

    if item.seriesid:
        seasons = current_session.get('https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-tv-seasons?bySeriesId=' + item.seriesid).json()['entries']
        for season in seasons:
            if 'mediasettvseason$brandId' in season and 'mediasettvseason$displaySeason' in season:
                itemlist.append(
                    item.clone(seriesid = '',
                               title=support.typo(season['mediasettvseason$displaySeason'], 'bold'),
                               urls=season['mediasettvseason$brandId']))
        itemlist = sorted(itemlist, key=lambda it: it.title, reverse=True)
        if len(itemlist) == 1: return epmenu(itemlist[0])
    if not itemlist:
        entries = current_session.get('https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-brands?byCustomValue={brandId}{' + item.urls + '}').json()['entries']
        for entry in entries:
            if 'mediasetprogram$subBrandId' in entry:
                itemlist.append(
                    item.clone(action='episodios',
                               title=support.typo(entry['description'], 'bold'),
                               url=entry['mediasetprogram$subBrandId'],
                               order=entry.get('mediasetprogram$order',0)))
        if len(itemlist) == 1: return episodios(itemlist[0])
        itemlist = sorted(itemlist, key=lambda it: it.order)
    return itemlist


def episodios(item):
    logger.debug()
    itemlist = []
    if not item.nextIndex: item.nextIndex = 1

    url = 'https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-programs?byCustomValue={subBrandId}{'+ item.url + '}&range=' + str(item.nextIndex) + '-' + str(item.nextIndex + PAGINATION)
    json = current_session.get(url).json()['entries']

    for it in json:
        urls = []
        if 'media' in it:
            for key in it['media']:
                urls.append(key['publicUrl'])
        if urls:
            title = it['title']
            itemlist.append(
                item.clone(action='findvideos',
                           title=support.typo(title, 'bold'),
                           contentType='episode',
                           thumbnail=it['thumbnails']['image_vertical-264x396']['url'] if 'image_vertical-264x396' in it['thumbnails'] else '',
                           fanart=it['thumbnails']['image_keyframe_poster-1280x720']['url'] if 'image_keyframe_poster-1280x720' in it['thumbnails'] else '',
                           plot=it['longDescription'] if 'longDescription' in it else it['description'],
                           urls=urls,
                           url=it['mediasetprogram$pageUrl'],
                           year=it.get('year',''),
                           ep= it.get('tvSeasonEpisodeNumber', 0) if it.get('tvSeasonEpisodeNumber', 0) else 0,
                           forcethumb=True,
                           no_return=True))

    if len(itemlist) == 1: return findvideos(itemlist[0])

    if (len(json) >= PAGINATION):
        item.nextIndex += PAGINATION + 1
        support.nextPage(itemlist, item)

    return itemlist


def findvideos(item):
    logger.debug()
    itemlist = [item.clone(server='directo', title='Mediaset Play', urls=item.urls, action='play')]
    return support.server(item, itemlist=itemlist, Download=False)


def play(item):
    logger.debug()
    for url in item.urls:
        sec_data = support.match(url + post_url).data
        item.url = support.match(sec_data, patron=r'<video src="([^"]+)').match
        pid = support.match(sec_data, patron=r'pid=([^|]+)').match
        item.manifest = 'mpd'

        if pid:
            item.drm = 'com.widevine.alpha'
            item.license = lic_url % pid
        break

    return [item]


def subBrand(json):
    logger.debug()
    subBrandId = current_session.get('https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-brands?byCustomValue={brandId}{' + json + '}').json()['entries'][-1]['mediasetprogram$subBrandId']
    json = current_session.get('https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-programs?byCustomValue={subBrandId}{' + subBrandId + '}').json()['entries']
    return json


def get_from_id(item):
    logger.debug()
    json = current_session.get(entry.format(id=item.url)).json()
    if 'components' in json:
        id = quote(",".join(json["components"]))
        json = current_session.get(entries.format(id=id)).json()
    if 'entries' in json:
        return json['entries']
    return {}


def get_programs(item, ret=[], args={}):
    hasMore = False
    url = ''

    if 'search' in item.args:
        args['uxReference'] = item.args[2]
        args["query"] = item.text
        args['traceCid'] = tracecid
        args['cwId'] = cwid
        args['page'] = 1
        args['platform'] = 'pc'
        args['hitsPerPage'] = 500
        url = 'https://api-ott-prod-fe.mediaset.net/PROD/play/rec2/search/v1.0?' + urlencode(args)
    elif not args:
        if item.ref in cdict:
            args['uxReference'] = cdict[item.ref]
            args['platform'] = 'pc'
        else:
            args = {"query": "*:*"}
            if item.args[2]:
                args['categories'] = item.args[2]

        args['cwId'] = cwid
        args['traceCid'] = tracecid
        args['hitsPerPage'] = 500
        args['page'] = '0'
        args['deviceId'] = deviceid
        url="https://api-ott-prod-fe.mediaset.net/PROD/play/rec2/cataloguelisting/v1.0?" + urlencode(args)

    # if 'all' in item.args: url = 'https://api-ott-prod-fe.mediaset.net/PROD/play/rec/azlisting/v1.0?' + urlencode(args)
    if url:
        json = current_session.get(url).json()
        if 'response' in json:
            json = json['response']
        if 'hasMore' in json:
            hasMore = json['hasMore']
        if 'components' in json:
            id = quote(",".join(json["components"]))
            json = current_session.get(entries.format(id=id)).json()
        if 'entries' in json:
            ret += json['entries']
        if hasMore:
            args['page'] = str(int(args['page']) + 1)
            return get_programs(item, ret, args)
        else:
            return ret
    else:
        return ret
