import sys
from multiprocessing import Pool
import requests
from bs4 import BeautifulSoup


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
        return self.HEADER + text + self.ENDC

    def bold(self, text):
        return self.BOLD + text + self.ENDC

c = Colors()


def poke_link(url):
    request = requests.get(url)
    feedback = '[{}] {}'.format(request.status_code, url)
    if request.status_code == 200:
        feedback = c.success(feedback)
    else:
        feedback = c.fail(feedback)
    print(feedback)


def poke_page(url):
    if not url.startswith("http:"):
        url = "http://" + url
    print(c.bold(url))

    r = requests.get(url)
    if r.status_code != 200:
        print(c.fail("Bad input url ({})".format(r.status_code)))
        return False

    soup = BeautifulSoup(r.text)
    link_urls = [a.get('href') for a in soup.find_all('a')]
    p = Pool(4)
    p.map(poke_link, link_urls)

if __name__ == "__main__":
    print(c.header("--- LinkPoke ---"))
    if len(sys.argv) == 1:
        print(c.bold("Usage: python poke.py [http://]poke.this/here"))
    else:
        poke_page(sys.argv[1])
