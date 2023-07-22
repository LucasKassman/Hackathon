import requests
from math import sin, cos, sqrt, atan2, radians

# Input:
#  ipAddr : String in dot notation, i.e. "8.8.8.8"
# Output:
#  {"country":"United States","countryCode":"US","lat":33.7671,"lon":-118.3814}
def getLocation(ipAddr):
    endPoint = 'http://ip-api.com/json/%s?fields=country,countryCode,lat,lon'%(ipAddr)
    print(endPoint)
    response = requests.get(endPoint)
    json = response.json()
    return json

def distance(lat1,lon1,lat2,lon2):
    R = 6373.0  # Earth radius in Km
    rlat1 = radians(lat1)
    rlon1 = radians(lon1)
    rlat2 = radians(lat2)
    rlon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance # Km


#json1 = getLocation('47.180.97.132') # California
#print(json1)
#json2 = getLocation('4.68.111.101')  # Arkansas
#print(json2)
#dist = distance(json1.get('lat',0),json1.get('lon',0),json2.get('lat',0),json2.get('lon',0))
#print(dist)

