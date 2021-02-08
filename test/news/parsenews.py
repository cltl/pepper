from __future__ import print_function, unicode_literals

from bs4 import BeautifulSoup
import requests

from xml.etree import ElementTree

import time
import json
import os
import io
import re


class Article(object):
    def __init__(self, language, time, url, title, publisher, author, raw):
        self.language = language
        self.title = title
        self.publisher = publisher
        self.author = author
        self.time = time
        self.url = url
        self.raw = raw

        self.hash = str(abs(hash(self.url)))

    @property
    def complete(self):
        return self.language and self.time and self.url

    def to_dict(self):
        return {
            'language': self.language,
            'title': self.title,
            'publisher': self.publisher,
            'author': self.author,
            'time': self.time,
            'url': self.url,
            'raw': self.raw,
            'hash': self.hash
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_naf(self):
        xml_header = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'

        naf = ElementTree.Element("NAF")
        naf.set("version", "v3")
        naf.set("xml:lang", self.language)

        header = ElementTree.SubElement(naf, "nafHeader")

        file_desc = ElementTree.SubElement(header, "fileDesc")
        file_desc.set("creationtime", self.time)

        if self.publisher: file_desc.set("publisher", self.publisher)
        if self.author: file_desc.set("author", self.author)
        if self.title: file_desc.set("title", self.title)

        public = ElementTree.SubElement(header, "public")
        public.set("uri", self.url)

        raw = ElementTree.SubElement(naf, "raw")

        # Add CData via Comment Hack (Add as Comment, then remove Comment Tags in the End)
        raw.append(ElementTree.Comment("<![CDATA[{}]]>".format(self.raw)))

        output = xml_header + ElementTree.tostring(naf)

        # Remove Comment (See CData Hack)
        return output.replace('<!--', "").replace("-->", "")


def parse_author(html):
    html = BeautifulSoup(html, 'html.parser')

    result = ""

    # Try Parsing Author from Meta Tags
    author = html.find('meta', attrs={'name': re.compile('author')}) or \
             html.find('meta', property=re.compile('author', re.IGNORECASE))

    if author: result = author['content']
    else:  # Otherwise, try parsing Author from Text
        author = html.find(attrs={'itemprop': 'author'}) or \
                 html.find(attrs={'class': 'byline'})
        if author: result = author.text

    return re.sub(r"\s+", " ", re.sub("by ", "", result, flags=re.IGNORECASE)).strip()


def parse_news(html):
    author = parse_author(html)

    html = BeautifulSoup(html, 'html.parser')

    # Try to find Article Body by Semantic Tag
    article = html.find('article')

    # Otherwise, try to find Article Body by Class Name (with the largest number of paragraphs)
    if not article:
        articles = html.find_all(class_=re.compile('(body|article|main)', re.IGNORECASE))
        if articles:
            article = sorted(articles, key=lambda x: len(x.find_all('p')), reverse=True)[0]

    # Parse text from all Paragraphs
    text = []
    if article:
        for paragraph in [tag.text for tag in article.find_all('p')]:
            if re.findall("[.,!?]", paragraph):
                text.append(paragraph)
    text = re.sub(r"\s+", " ", " ".join(text))

    return author, text


def get_news(query, language='en', region='us', cache=True):
    """
    Get News Articles from Google News

    Parameters
    ----------
    query: str
        The Search Term
    language: str
        Search Language
    region: str
        Search Region
    cache: bool
        Use Cached Results (if Available)
    """

    query = query.lower()

    # Create Cache
    cache_root = os.path.join('tmp', "{}".format(query), "{}-{}".format(language, region))
    if not os.path.exists(cache_root):
        os.makedirs(cache_root)

    # If no cache exists or user wants to rebuild cache
    if not cache or not len(os.listdir(cache_root)):

        base_url = "http://news.google.com"
        query_url = "{0}/?q={1}&hl={1}-{2}&gl={2}".format(base_url, query, language, region)

        # Create Content Parser (Beautiful Soup)
        soup = BeautifulSoup(requests.get(query_url).content, 'html.parser')

        # Remove Existing Cache
        for item in os.listdir(cache_root):
            os.remove(os.path.join(cache_root, item))

        # Iterate over all Articles in Google News
        articles = soup.find_all('article')
        for i, article in enumerate(articles, 1):
            div, title, publisher = article.find_all('a')

            time = re.sub("[Z\-:]", "", article.find('time').get('datetime'))

            article_redirect = "{}{}".format(base_url, title.get('href')[1:])
            article_url = requests.get(article_redirect).url
            article_hash = int(abs(hash(article_url)))

            print("\r[{:3d}/{:3d}] Downloading {}".format(i, len(articles), article_url), end="")

            # Write Json Metadata to Cache
            with open(os.path.join(cache_root, "{}.json".format(article_hash)), 'w') as json_file:
                json.dump({'title': title.text, 'publisher': publisher.text, 'time': time, 'url': article_url}, json_file)

            # Write HTML to Cache
            with open(os.path.join(cache_root, "{}.html".format(article_hash)), 'w') as html:
                html.write(requests.get(article_url).content)

    json_files = [item for item in os.listdir(cache_root) if item.endswith('json')]
    for i, path in enumerate(json_files, 1):

        full_path_json = os.path.join(cache_root, path)
        full_path_html = full_path_json.replace('.json', '.html')

        with open(full_path_json) as json_file, open(full_path_html) as html_file:
            data = json.load(json_file)

            print("\r[{:3d}/{:3d}] Parsing {}".format(i, len(json_files), data['url']), end="")

            yield Article(language, data['time'], data['url'], data['title'], data['publisher'], *parse_news(html_file.read()))


def news_to_naf(articles, path):
    if not os.path.exists(path):
        os.makedirs(path)

    for article in articles:
        if article.complete:
            xml_path = os.path.join(path, "{}.xml".format(article.hash))
            with io.open(xml_path, 'w', encoding='utf-8') as xml_file:
                xml_file.write(article.to_naf())


if __name__ == '__main__':

    DIR = 'tmp/brexit/en-gb-json'

    # # Get News and Save as JSON
    # for item in get_news('brexit', 'en', 'gb'):
    #     with open('tmp/brexit/en-gb-json/{}.json'.format(item.hash), 'w') as json_file:
    #         json_file.write(item.to_json())


    def strip_nonascii(text):
        return re.sub(r'[^\x00-\x7F]+', ' ', text)


    print("BREXIT_NEWS = [")
    for item in os.listdir(DIR):
        with open(os.path.join(DIR, item)) as json_file:
            article = json.load(json_file)
            if all([key in article for key in 'author', 'title', 'publisher', 'time']):
                date = time.strftime('%A %B %d', time.strptime(article['time'], '%Y%m%dT%H%M%S'))
                if article['author'] and article['title'] and article['publisher'] and article['time']:
                    print('    "On {}, {} wrote an article in {} titled: {}",'.format(
                        date,
                        strip_nonascii(article['author']),
                        strip_nonascii(article['publisher']),
                        strip_nonascii(article['title'])).replace(':', ':...'))
    print("]")
