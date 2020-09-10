import re
import requests

from bs4 import BeautifulSoup

class WebPage:
    def __get_qdn(self, url):
        qdn = ''

        if url.startswith('http://'):
            qdn = url[7:].split('/')[0]
        elif url.startswith('https://'):
            qdn = url[8:].split('/')[0]
        else:
            qdn = url.split('/')[0]

        return qdn

    def __init__(self, url):
        self.url = url
        self.qdn = self.__get_qdn(url)


class WebPageDownloader:
    def __download_page(self):
        # Download the webpage
        r = requests.get(self.webpage.url)
        if r is None or r.status_code != 200 or r.text is None:
            return None

        if r.encoding is not None and r.encoding.startswith('ISO-8859'):
            r.encoding = 'UTF-8'

        return r

    def is_valid(self):
        return self.r is not None
    
    def get_text(self):
        if self.r is not None:
            return self.r.text

        return ''

    def __init__(self, webpage):
        self.webpage = webpage
        self.r = self.__download_page()

class WebPageLinkExtractor:
    def __init__(self, webpage):
        downloader = WebPageDownloader(webpage)

        self.internal_links = []
        self.external_links = []

        tree = BeautifulSoup(downloader.get_text(), 'lxml')
        for link in tree.find_all('a'):
            if 'href' not in link.attrs:
                continue

            url = link.attrs['href']
            if url.startswith('#') or url.startswith('mailto') or url.startswith('?'):
                continue

            if url.startswith('//'):
                url = 'http:' + url
            elif url.startswith('/'):
                url = 'http://' + webpage.qdn + url
            elif url.startswith('./'): 
                url = 'http://' + webpage.qdn + url[1:]
            elif url.startswith('/'):
                url = 'http://' + webpage.qdn + url
            elif not url.startswith('http'):
                url = 'http://' + webpage.qdn + '/' + url


            w = WebPage(url)
            if w.qdn == webpage.qdn:
                self.internal_links.append(w)
            else:
                self.external_links.append(w)

