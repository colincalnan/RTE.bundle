####################################################################################################

VIDEO_PREFIX = "/video/rte"

NAME = L('RTE')

ART  = 'art-default.jpg'
ICON = 'icon-default.png'

FEEDBASE = "http://dj.rte.ie/vodfeeds/feedgenerator/"
LIVEURL = "http://www.rte.ie/player/live/7" #"http://www.rte.ie/player/#l=7"

MRSS  = {'media':'http://search.yahoo.com/mrss/'}
RTE   = {'rte':'http://www.rte.ie/schemas/vod'}

####################################################################################################
def Start():
    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = NAME
    DirectoryObject.thumb = R(ICON)
    
    Dict['geo_code']=str(Geo())

####################################################################################################
@route('/video/rte/geo')
def Geo():
    country_code = HTML.ElementFromURL(FEEDBASE+'cl/').xpath("//geoinfo/country")[0]
    if country_code.text == "ie":
      return "#domestic"
    else:
      return "#international"

####################################################################################################
@route('/video/rte/updatecache')
def UpdateCache():
  HTTP.PreCache(FEEDBASE + "videos/live/?id=7")
  HTTP.PreCache(FEEDBASE + "latest/?limit=20")
  HTTP.PreCache(FEEDBASE + "lastchance/?limit=20")
  HTTP.PreCache(FEEDBASE + "genre/?id=Entertainment")
  HTTP.PreCache(FEEDBASE + "genre/?id=Drama")
  HTTP.PreCache(FEEDBASE + "genre/?id=News%20and%20Sport")
  HTTP.PreCache(FEEDBASE + "genre/?id=Factual")
  HTTP.PreCache(FEEDBASE + "genre/?id=Lifestyle")
  HTTP.PreCache(FEEDBASE + "genre/?id=Arts%20and%20Music")
  HTTP.PreCache(FEEDBASE + "genre/?id=Religious%20and%20Irish%20Language")
  HTTP.PreCache(FEEDBASE + "genre/?id=RT%C3%89jr%2C%20TRT%C3%89%2C%20Two%20Tube")

####################################################################################################
@handler('/video/rte', NAME, thumb=ICON, art=ART)
def MainMenu():
    oc = ObjectContainer()
    
    #Live Stream
    if Platform.HasFlash:
        feed = RSS.FeedFromURL(FEEDBASE + "videos/live/?id=7")
        desc = feed.entries[0].description
        thumb = feed.entries[0].media_thumbnail[0]['url']
        link = LIVEURL + Dict['geo_code']
        oc.add(VideoClipObject(url=link, title="Live", summary=desc, thumb=thumb)) 

    oc.add(DirectoryObject(key=Callback(RSS_parser, pageurl=FEEDBASE+"latest/?limit=20", title="Latest"), title="Latest"))
    oc.add(DirectoryObject(key=Callback(RSS_parser, pageurl=FEEDBASE+"lastchance/?limit=20", title="Last Chance"), title="Last Chance"))
    oc.add(DirectoryObject(key=Callback(CategoriesSubMenu), title="Categories"))
    oc.add(DirectoryObject(key=Callback(AZSubMenu), title="A to Z"))
    
    return oc

####################################################################################################
@route('/video/rte/categories')
def CategoriesSubMenu():
    oc = ObjectContainer(title2="Categories")

    oc.add(DirectoryObject(key=Callback(RSS_parser, pageurl=FEEDBASE+"genre/?id=Entertainment", title="Entertainment"), title="Entertainment"))
    oc.add(DirectoryObject(key=Callback(RSS_parser, pageurl=FEEDBASE+"genre/?id=Drama", title="Drama"), title="Drama"))
    oc.add(DirectoryObject(key=Callback(RSS_parser, pageurl=FEEDBASE+"genre/?id=News%20and%20Sport", title="News and Sporst"), title="News and Sports"))
    oc.add(DirectoryObject(key=Callback(RSS_parser, pageurl=FEEDBASE+"genre/?id=Factual", title="Factual"), title="Factual"))
    oc.add(DirectoryObject(key=Callback(RSS_parser, pageurl=FEEDBASE+"genre/?id=Lifestyle", title="Lifestyle"), title="Lifestyle"))
    oc.add(DirectoryObject(key=Callback(RSS_parser, pageurl=FEEDBASE+"genre/?id=Arts%20and%20Music", title="Arts and Music"), title="Arts and Music"))
    oc.add(DirectoryObject(key=Callback(RSS_parser, pageurl=FEEDBASE+"genre/?id=Religious%20and%20Irish%20Language", title="Religious and Irish language"), title="Religious and Irish language"))
    oc.add(DirectoryObject(key=Callback(RSS_parser, pageurl=FEEDBASE+"genre/?id=RT%C3%89jr%2C%20TRT%C3%89%2C%20Two%20Tube", title=u"RT\u00C9jr, TRT\u00C9, Two Tube"), title=u"RT\u00C9jr, TRT\u00C9, Two Tube")) 

    return oc

####################################################################################################
@route('/video/rte/atoz')
def AZSubMenu():
    oc = ObjectContainer(title2="A to Z")

    for entry in HTML.ElementFromURL(FEEDBASE+'azlist/').xpath("//entry"):
        if entry.xpath("title")[0].text == None:
            continue
        else:
            character = entry.xpath("title")[0].text
        oc.add(DirectoryObject(key=Callback(RSS_parser, pageurl=FEEDBASE+'az/?id='+character, title=character), title=character))

    return oc

####################################################################################################
@route('/video/rte/rss')
def RSS_parser(pageurl, title):
    oc = ObjectContainer(title2=title)

    feed = RSS.FeedFromURL(pageurl)
    i = 0
    while i < len(feed.entries):
        title = feed.entries[i].title
        desc = feed.entries[i].description
        duration = int(feed.entries[i].rte_duration['ms'])
        thumb = feed.entries[i].media_thumbnail[0]['url']
        link = feed.entries[i].id
        oc.add(VideoClipObject(url=link, title=title, summary=desc, duration=duration, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))
        i = i+1

    if len(oc) < 1:
        return ObjectContainer(header="Empty", message="No content found.")
    return oc
