import urllib
import urllib2
import simplejson

def findaddress(query):
    url = "http://nominatim.openstreetmap.org/search/%s"%(query)
    data = urllib.urlencode({"format": "json"})
    f = urllib2.urlopen(url + "?" + data)
    result = f.read()
    best_match = simplejson.loads(result)[0]
    print best_match["lat"], best_match["lon"]
