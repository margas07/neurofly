import urllib.request, json, math

with urllib.request.urlopen("http://192.168.43.1:8080/get?status&lat&lon&z&zwgs84&v&dir&dist&diststart&accuracy&zAccuracy&satellites") as url:
    data = json.load(url)
    print(data)
    lat = data["buffer"]["lat"]["buffer"][0]
    print(lat)
    lon = data["buffer"]["lon"]["buffer"][0]
    print(lon)
    hei = data["buffer"]["z"]["buffer"][0]
    print(hei)
    
    vel = data["buffer"]["v"]["buffer"][0]
    print(vel)
    direct = data["buffer"]["dir"]["buffer"][0]
    print(direct)