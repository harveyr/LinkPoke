import sys
from multiprocessing import Pool
import requests
import urlparse
from bs4 import BeautifulSoup
import signal


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

    def success(self, text):
        return self.OKGREEN + text + self.ENDC

    def warn(self, text):
        return self.WARNING + text + self.ENDC

    def fail(self, text):
        return self.FAIL + text + self.ENDC

    def header(self, text):
        return self.OKBLUE + text + self.ENDC

    def bold(self, text):
        return self.BOLD + text + self.ENDC

c = Colors()


def poke_link(url):
    """Need this outside of the LinkPoker class so that multiprocessing can
    map to it. Otherwise there's a pickle error."""
    try:
        request = requests.get(url)
        feedback = '[{}] {}'.format(request.status_code, url)
        if request.status_code == 200:
            feedback = c.success(feedback)
        else:
            feedback = c.fail(feedback)
        print(feedback)
    except requests.exceptions.ConnectionError as e:
        print(c.fail('[Error] {}\n{}\n'.format(url, e)))


class LinkPoker:

    def __init__(self, url):
        self.url = url
        self.parsed_url = urlparse.urlparse(url)
        request = requests.get(url)
        if request.status_code != 200:
            raise Exception(
                "Bad status code for input url: {}".format(request.status_code))
        self.soup = BeautifulSoup(request.text)

    def absolute_url(self, link_url):
        if link_url[0] in ['/', '#']:
            if link_url[0] == '#':
                link_url = '/' + link_url
            return "{scheme}://{netloc}{link}".format(
                scheme=self.parsed_url.scheme,
                netloc=self.parsed_url.netloc,
                link=link_url)
        else:
            return link_url

    def poke(self):
        link_urls = set(map(
            self.absolute_url,
            [a.get('href') for a in self.soup.find_all('a')]))
        self.pool = Pool(4)
        self.pool.map(poke_link, link_urls)

    def stop(self):
        self.pool.terminate()


if __name__ == "__main__":
    print(c.header("--- LinkPoke ---"))
    if len(sys.argv) == 1:
        print(c.bold("Usage: python poke.py [http://]poke.this/here"))
        sys.exit()

    url = sys.argv[1]
    poker = LinkPoker(url)
    print(c.bold(url))

    def signal_handler(signal, frame):
        poker.stop()
        print(c.warn("\nAdios."))
        sys.exit()
    signal.signal(signal.SIGINT, signal_handler)

    poker.poke()
