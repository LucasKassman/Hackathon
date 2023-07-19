import requests

def getLocation(ipAddr):
    endPoint = 'http://ip-api.com/json/%s?fields=country,countryCode,lat,lon'%(ipAddr)
    print(endPoint)
    response = requests.get(endPoint)
    json = response.json()
    return json


#json = getLocation('47.180.97.132')
#print(json)
