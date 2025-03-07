# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Canale per AnimeSaturn
# ----------------------------------------------------------

from lib import js2py
from core import support
from platformcode import config

host = support.config.get_channel_url()
headers={'X-Requested-With': 'XMLHttpRequest'}

@support.menu
def mainlist(item):

    anime = ['/animelist?load_all=1&d=1',
             ('ITA',['', 'submenu', '/filter?language%5B0%5D=1']),
             ('SUB-ITA',['', 'submenu', '/filter?language%5B0%5D=0']),
             ('Più Votati',['/toplist','menu', 'top']),
             ('In Corso',['/animeincorso','peliculas','incorso']),
             ('Ultimi Episodi',['/fetch_pages.php?request=episodes&d=1','peliculas','updated'])]

    return locals()


def search(item, texto):
    support.info(texto)
    item.url = host + '/animelist?search=' + texto
    item.contentType = 'tvshow'
    try:
        return peliculas(item)
    # Continua la ricerca in caso di errore
    except:
        import sys
        for line in sys.exc_info():
            support.logger.error("%s" % line)
        return []


def newest(categoria):
    support.info()
    itemlist = []
    item = support.Item()
    try:
        if categoria == "anime":
            item.url = host + '/fetch_pages.php?request=episodes&d=1'
            item.args = "updated"
            return peliculas(item)
    # Continua la ricerca in caso di errore
    except:
        import sys
        for line in sys.exc_info():
            support.logger.error("{0}".format(line))
        return []

    return itemlist


@support.scrape
def submenu(item):
    data = support.match(item.url + item.args).data
    action = 'filter'
    patronMenu = r'<h5 class="[^"]+">(?P<title>[^<]+)[^>]+>[^>]+>\s*<select id="(?P<parameter>[^"]+)"[^>]+>(?P<data>.*?)</select>'
    def itemlistHook(itemlist):
        itemlist.insert(0, item.clone(title=support.typo('Tutti','bold'), url=item.url + item.args, action='peliculas'))
        return itemlist[:-1]
    return locals()


def filter(item):
    itemlist = []
    matches = support.match(item.data if item.data else item.url, patron=r'<option value="(?P<value>[^"]+)"[^>]*>(?P<title>[^<]+)').matches
    for value, title in matches:
        itemlist.append(item.clone(title= support.typo(title,'bold'), url='{}{}&{}%5B0%5D={}'.format(host, item.args, item.parameter, value), action='peliculas', args='filter'))
    support.thumb(itemlist, genre=True)
    return itemlist


@support.scrape
def menu(item):
    patronMenu = r'<div class="col-md-13 bg-dark-as-box-shadow p-2 text-white text-center">(?P<title>[^"<]+)<(?P<other>.*?)(?:"lista-top"|"clearfix")'
    action = 'peliculas'
    item.args = 'top'
    def itemHook(item2):
        item2.url = item.url
        return item2

    return locals()


@support.scrape
def peliculas(item):
    anime = True

    deflang= 'Sub-ITA'
    action = 'check'
    page = None
    post = "page=" + str(item.page if item.page else 1) if item.page and int(item.page) > 1 else None

    if item.args == 'top':
        data = item.other
        patron = r'light">(?P<title2>[^<]+)</div>\s*(?P<title>[^<]+)[^>]+>[^>]+>\s*<a href="(?P<url>[^"]+)">(?:<a[^>]+>|\s*)<img.*?src="(?P<thumb>[^"]+)"'
    else:
        data = support.match(item, post=post, headers=headers).data
        if item.args == 'updated':
            page = support.match(data, patron=r'data-page="(\d+)" title="Next">').match
            patron = r'<a href="(?P<url>[^"]+)" title="(?P<title>[^"(]+)(?:\s*\((?P<year>\d+)\))?(?:\s*\((?P<lang>[A-Za-z-]+)\))?">\s*<img src="(?P<thumb>[^"]+)"[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>\s\s*(?P<type>[^\s]+)\s*(?P<episode>\d+)'
            typeContentDict = {'Movie':'movie', 'Episodio':'episode'} #item.contentType='episode'
            action = 'findvideos'
            def itemlistHook(itemlist):
                if page:
                    itemlist.append(item.clone(title=support.typo(support.config.get_localized_string(30992), 'color kod bold'),page= page, thumbnail=support.thumb()))
                return itemlist
        elif 'filter' in item.args:
            page = support.match(data, patron=r'totalPages:\s*(\d+)').match
            patron = r'<a href="(?P<url>[^"]+)" title="(?P<title>[^"(]+)(?:\s*\((?P<year>\d+)\))?(?:\s*\((?P<lang>[A-Za-z-]+)\))?">\s*<img src="(?P<thumb>[^"]+)"'
            def itemlistHook(itemlist):
                if item.nextpage: item.nextpage += 1
                else: item.nextpage = 2
                if page and item.nextpage < int(page):
                    itemlist.append(item.clone(title=support.typo(support.config.get_localized_string(30992), 'color kod bold'), url= '{}&page={}'.format(item.url, item.nextpage), infoLabels={}, thumbnail=support.thumb()))
                return itemlist

        else:
            pagination = ''
            if item.args == 'incorso':
                patron = r'<a href="(?P<url>[^"]+)"[^>]+>(?P<title>[^<(]+)(?:\s*\((?P<year>\d+)\))?(?:\s*\((?P<lang>[A-za-z-]+)\))?</a>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>\s*<img width="[^"]+" height="[^"]+" src="(?P<thumb>[^"]+)"[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>(?P<plot>[^<]+)<'
            else:
                # debug=True
                patron = r'<img src="(?P<thumb>[^"]+)" alt="(?P<title>[^"\(]+)(?:\((?P<lang>[Ii][Tt][Aa])\))?(?:\s*\((?P<year>\d+)\))?[^"]*"[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>\s*<a class="[^"]+" href="(?P<url>[^"]+)">[^>]+>[^>]+>[^>]+>\s*<p[^>]+>(?:(?P<plot>[^<]+))?<'

    return locals()


def check(item):
    movie = support.match(item, patron=r'Episodi:</b> (\d*) Movie')
    if movie.match:
        episodes = episodios(item)
        if len(episodes) > 0:
            it = episodes[0].clone(contentType = 'movie', contentTitle=item.fulltitle, contentSerieName='')
        return findvideos(it)
    else:
        item.contentType = 'tvshow'
        return episodios(item)


@support.scrape
def episodios(item):
    if item.contentType != 'movie': anime = True
    patron = r'episodi-link-button">\s*<a href="(?P<url>[^"]+)"[^>]+>\s*(?P<title>[^<]+)</a>'
    return locals()


def findvideos(item):
    support.info()
    itemlist = []
    links = []
    # page_data = ''
    # titles =['Primario', 'Secondario', 'Alternativo Primario', 'Alternativo Secondario']
    # pre_data = support.match(item, headers=headers).data
    # url = support.match(pre_data , patron=r'<a href="([^"]+)">[^>]+>[^>]+>G').match
    # urls = [url, url+'&extra=1', url+'&s=alt', url+'&s=alt&extra=1']
    # links = []
    # support.dbg()
    # for i, url in enumerate(urls):
    #     data = support.match(url, headers=headers).data
    #     if not '&s' in url:
    #         link = support.match(data, patron=r'(?:<source type="[^"]+"\s*src=|file:\s*)"([^"]+)"', headers=headers).match
    #     else:
    #         link = support.match(data, headers=headers, patron=r'file:\s*"([^"]+)"').match
    #     if not link:
    #         page_data += data
    #     if link and link not in links:
    #         links.append(link)
    #         # link += '|Referer=' + item.url
    #         itemlist.append(item.clone(action="play", title=titles[i], url=link, server='directo'))

    # return support.server(item, data=data, itemlist=itemlist)
    main_url = support.match(item, patron=r'<a href="([^"]+)">[^>]+>[^>]+>G').match
    # internal = support.match(data, patron=r'<a href="([^"]+)">[^>]+>[^>]+>G').match
    urls = support.match(support.match(main_url, headers=headers).data, patron=r'<a class="dropdown-item"\s*href="([^"]+)', headers=headers).matches
    itemlist.append(item.clone(action="play", title='Primario', url=main_url, server='directo'))
    itemlist.append(item.clone(action="play", title='Secondario', url=main_url + '&s=alt', server='directo'))
    # support.dbg()
    # for i, url in enumerate(internal_urls):
    #     internal_data = support.match(url, headers=headers).data
    #     if not '&s' in url:
    #         link = support.match(internal_data, patron=r'(?:<source type="[^"]+"\s*src=|file:\s*)"([^"]+)"', headers=headers).match
    #     else:
    #         link = support.match(internal_data, headers=headers, patron=r'file:\s*"([^"]+)"').match
    #     if not link:
    #         links.append(internal_data)
    #     if link and link not in links:
    #         links.append(link)
    #         itemlist.append(item.clone(action="play", title=internal_titles[i], url=link, server='directo'))
    # link = support.match(external[0], patron=r'href="([^"]+)', headers=headers, debug=True).match
    # support.dbg()
    for url in urls:
        link = support.match(url, patron=r'<a href="([^"]+)"[^>]+><button', headers=headers).match
        if link:
            links.append(link)
    return support.server(item, data=links, itemlist=itemlist)









