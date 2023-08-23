import requests, urllib.parse, re, urllib3
from bs4 import BeautifulSoup


def nextLink(url, href, index_link):        
    link = index_link 
    if len([_ for _ in href.get('href').replace('%2F', '/').split('/') if _])==1:
        link +=  url.replace(index_link, '')
    link +=  '/' + href.get('href')
    return link


def getRequest(url, max_tries=3):
    encoded_url = urllib.parse.quote(url, safe=':/%=+-')
    for i in range(max_tries):
        try:
            return requests.get(encoded_url, stream=True, timeout=5)
        
        except requests.exceptions.MissingSchema:
            return -1
        
        except Exception as e:
            pass
    return -1


def get_index_link(url, check_only=None):
    if not check_only:
        r = getRequest(url)
        if r==-1:
            return 
    try:
        return re.search(r'http[s]{,1}://.*?/', url).group(0)
    except Exception as e:
        return 
