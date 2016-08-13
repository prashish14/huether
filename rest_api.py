from flask import Flask
from flask_restful import Resource, Api
from flask import make_response
from flask_restful import reqparse
import weather
import json


app = Flask(__name__)



api = Api(app)
global huether
huether = weather.Huether()

callback="jQuery310098894939246408_1471076458600"
_="1471076458601"

class SetZipCode(Resource):
    def put(self):
        global huether
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('zip', type=str,help='Users zipcode')
            parser.add_argument('cc', type=str,help='Users countrycode')

            args = parser.parse_args()
            _zip = args['zip']
            _cc = args['cc'] #country code

            huether.setLocation(_zip,_cc)
            #RGB={'r':255,'g':255,'b':255}
            print 'test'
            response = make_response(json.dumps(huether.getWeather('setup')))
            #self.after_request(response)

        except Exception as e:
            return {'ERROR': str(e)}

    def after_request(self, response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        print response
        return response

class SetWeather(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('weather',type=str)
            args = parser.parse_args()

            _weather = args['weather']
            RGB = huether.weatherToRGB(_weather)
            huether.hue.changeGroupLight(RGB,group=3)
        except Exception as e:
            print "ERROR: " + str(e)


class WeatherInfo(Resource):
    def get(self):
        return huether.getWeather()


api.add_resource(SetZipCode,'/SetZipCode')
api.add_resource(SetWeather,'/SetWeather')
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
