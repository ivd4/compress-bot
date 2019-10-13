import requests
import ssl

from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urljoin


def get_files_from_link(url):
    try:
        html = requests.get(url).content
    except (ConnectionError, ssl.SSLError):
        return -1, 0, 0

    bs = BeautifulSoup(html, "html.parser", parse_only=SoupStrainer('a'))
    data_list = []
    names_list = []
    cnt = 0
    for link in bs:
        if link.has_attr('href') and link['href'].endswith(".txt"):
            cnt += 1
            curl = link['href']
            curl = urljoin(url, curl)
            names_list.append(curl.rsplit("/", 1)[-1])
            data_list.append(requests.get(curl).content)

    return cnt, names_list, data_list
