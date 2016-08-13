import urllib2
import json
import requests
import math
from collections import namedtuple
import time
import MySQLdb


XYPoint = namedtuple('XYPoint', ['x', 'y'])

class Huether (object):
    zipcode = 94115 #Default is San Francisco
    countrycode = 'us'
    appid ='f1f8fd92bac0a338d47b23800fd5b3fe'
    cur = None
    def __init__ (self):
        self.hue = HueLights()
        self.cur = MySQLdb.connect(host='localhost',
                                  user = 'root',
                                  passwd = 'root',
                                  db='heutherapp').cursor()

    def setLocation (self, zipcode, countrycode):
        self.zipcode = zipcode
        self.countrycode = countrycode

    def getWeather(self,req):
        #f = urllib2.urlopen('http://api.openweathermap.org/data/2.5/weather?zip={},{}&appid={}'.format(self.zipcode, \
        #                                                                                               self.countrycode, \
        #                                                                                               self.appid))
        #json_string = f.read()
        #weatherInfo = json.loads(json_string)
        #f.close()
        self.weatherToRGB('Cloudy')
        exit(1)
        #self.hue.setLightGroup(self,group=None)

        weatherInfo[unicode('main')][unicode('temp')] = str(self.kToF(int(weatherInfo[unicode('main')][unicode('temp')])))
        weatherInfo[unicode('main')][unicode('temp_min')] = str(self.kToF(int(weatherInfo[unicode('main')][unicode('temp_min')])))
        weatherInfo[unicode('main')][unicode('temp_max')] = str(self.kToF(int(weatherInfo[unicode('main')][unicode('temp_max')])))

        if req is not None:

            putInfo = weatherInfo[unicode('main')]
            putInfo[unicode('city')] = weatherInfo[unicode('name')]

            key='Sunny'
            self.weatherToRGB(key)
            return putInfo
        else:
            print 'IS NOT SETUP'
            return weatherInfo


    def weatherToRGB(self, key):
       self.cur.execute("SELECT * FROM heutherscences WHERE heutherscence = '{}';".format(key))
       data=self.cur.fetchall()
       print 'data' + str(data)
       RGB={'r':255,'g':255,'b':255}

       RGB['r']=int(data[0][1])
       RGB['g']=int(data[0][2])
       RGB['b']=int(data[0][3])
       return RGB

    def kToF(self,k):
        return float(k*9/5-459.67)

class HueLights (object):
    base_url = 'http://192.168.10.120/api/0HRFF6T37jaoXmmB5-1ZrMnTx8ewGYmn56B7rvuy'


    Red = XYPoint(0.675, 0.322)
    Lime = XYPoint(0.4091, 0.518)
    Blue = XYPoint(0.167, 0.04)

    def changeLight(self, light):
        url = self.base_url + '/lights/{}/state'.format(light['id'])
        body = {'on':True, 'xy_inc':self.getXYFromRGB(light['rgb'])}
        payload = json.dumps(body)
        r = requests.put(url,data=payload)
        print r.content

    def changeLights(self, lights):
        for light in lights:
            self.changeLight(light)

    def changeGroupLight(self,RGB,group=0):

        url = self.base_url + '/groups/{}/action'.format(group)
        xy = self.getXYFromRGB(RGB)

        body = {'on':True, 'xy_inc':xy}
        payload = json.dumps(body)
        r = requests.put(url,data=payload)
        print 'STATUS:' + str(r.status_code)
        print 'CONTENT: ' + str(r.content)



    def getXYFromRGB (self,RGB):
        r = ((RGB['r'] + 0.055) / (1.0 + 0.055))**2.4 if (RGB['r'] > 0.04045) else (RGB['r'] / 12.92)
        g = ((RGB['g'] + 0.055) / (1.0 + 0.055))**2.4 if (RGB['g'] > 0.04045) else (RGB['g'] / 12.92)
        b = ((RGB['b'] + 0.055) / (1.0 + 0.055))**2.4 if (RGB['b'] > 0.04045) else (RGB['b'] / 12.92)

        X = r * 0.4360747 + g * 0.3850649 + b * 0.0930804
        Y = r * 0.2225045 + g * 0.7168786 + b * 0.0406169
        Z = r * 0.0139322 + g * 0.0971045 + b * 0.7141733

        if X + Y + Z == 0:
            cx = cy = 0
        else:
            cx = X / (X + Y + Z)
            cy = Y / (X + Y + Z)

        xyPoint = XYPoint(cx, cy)
        inReachOfLamps = self.checkPointInLampsReach(xyPoint)

        if not inReachOfLamps:
            print 'NOT IN REACH OF LAMPS'
            xyPoint = self.getClosestPointToPoint(xyPoint)

        return xyPoint




    def getClosestPointToPoint(self, xyPoint):
        pAB = self.getClosestPointToLine(self.Red, self.Lime, xyPoint)
        pAC = self.getClosestPointToLine(self.Blue, self.Red, xyPoint)
        pBC = self.getClosestPointToLine(self.Lime, self.Blue, xyPoint)

        dAB = self.getDistanceBetweenTwoPoints(xyPoint, pAB)
        dAC = self.getDistanceBetweenTwoPoints(xyPoint, pAC)
        dBC = self.getDistanceBetweenTwoPoints(xyPoint, pBC)

        lowest = dAB
        closestPoint = pAB

        if (dAC < lowest):
            lowest = dAC
            closestPoint = pAC

        if (dBC < lowest):
            lowest = dBC
            closestPoint = pBC

        cx = closestPoint.x
        cy = closestPoint.y

        return XYPointChange(cx, cy)





    def getClosestPointToLine(self, A, B, P):
        AP = XYPoint(P.x - A.x, P.y - A.y)
        AB = XYPoint(B.x - A.x, B.y - A.y)
        ab2 = AB.x * AB.x + AB.y * AB.y
        ap_ab = AP.x * AB.x + AP.y * AB.y
        t = ap_ab / ab2

        if t < 0.0:
            t = 0.0
        elif t > 1.0:
            t = 1.0
        return XYPoint(A.x + AB.x * t, A.y + AB.y * t)

    def crossProduct(self, p1, p2):
        return (p1.x * p2.y - p1.y * p2.x)




    def checkPointInLampsReach(self, p):
        v1 = XYPoint(self.Lime.x - self.Red.x, self.Lime.y - self.Red.y)
        v2 = XYPoint(self.Blue.x - self.Red.x, self.Blue.y - self.Red.y)

        q = XYPoint(p.x - self.Red.x, p.y - self.Red.y)
        s = self.crossProduct(q, v2) / self.crossProduct(v1, v2)
        t = self.crossProduct(v1, q) / self.crossProduct(v1, v2)

        return (s >= 0.0) and (t >= 0.0) and (s + t <= 1.0)

#app = Huether()
#RGB = {'r':240,'g':103,'b':90}
#light = {'id':2,'rgb':RGB}
#app.hue.changeLight(light)
