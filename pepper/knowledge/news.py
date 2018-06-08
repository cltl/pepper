import requests
from random import choice


def get_headlines(country="us", category="science", key=r"fac63d98350243e2b4f6e51e4f42e13f"):
    return requests.get(r'https://newsapi.org/v2/top-headlines?country={}&category={}&apiKey={}'.format(country, category, key)).json()

def get_random_headline(country="us", category="science", key=r"fac63d98350243e2b4f6e51e4f42e13f"):
     return choice(get_headlines(country, category, key)['articles'])

if __name__ == "__main__":
    print(get_random_headline())