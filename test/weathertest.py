import requests
#import configparser
import json

from bs4 import BeautifulSoup

location = "Tokyo"

result = requests.get("https://www.google.com/search?q=weather+{}".format(location))

soup = BeautifulSoup(result.content, 'html.parser')

print(soup.find_all())
print()
print()
print()


def get_weather(api_key, location):
    url = "https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}".format(location, api_key)
    #url = "https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}".format(location, api_key)
    r = requests.get(url)
    return r.json()
    #already turns into a dictionary


def main():

    location = "Amsterdam"
    api_key = "4c7b59d98bcccad3ba39f5c73e28d009"

    weather = get_weather(api_key, location)

    #print("The temp is: ", weather['main']['temp'])
    #print(weather)
    #print(weather['weather'][0]['description'])

    #print("In {} it is {} and we have a maximum temperature of {} and a minimum temperature of {}".format(location,
    #weather['weather'][0]['description'], weather['main']['temp_max'], weather['main']['temp_min'])


    print("The weather in {} is {}, min temperature is {} and max temperature is {}".format(location,
        weather['weather'][0]['description'], weather['main']['temp_max'], weather['main']['temp_min']))

if __name__ == '__main__':
    main()



#PROGRAMMER'S TEMPORARY COMMENTS (PLEASE IGNORE)

#KEY
#4c7b59d98bcccad3ba39f5c73e28d009
#Look this link for format of the json file https://code-maven.com/openweathermap-api-using-python




#FOR INVALID ARGUMENTS
#if len(sys.argv) != 2:
        #exit("Usage: {} LOCATION".format(sys.argv[0]))
    #location = sys.argv[1]




#For thingy to parse json from https://linuxconfig.org/how-to-parse-data-from-json-into-python
#parsed_json = (json.loads(json_data))

# parsed_json = (json.loads(weather))
# print(json.dumps(parsed_json, indent=4, sort_keys=True))






