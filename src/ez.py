# encoding: utf-8

"""
eztv.it episode downloader by fox

example usage:
    ez.py family guy           will download most recent family guy ep
    ez.py marco polo s01e10    will download this specific episode
    ez.py top gear?            will show list of most recent top gear eps
    ez.py the wire s05?        will show list of season 5 episodes of the wire

"""

from bs4 import BeautifulSoup
from collections import namedtuple
import sys, requests, webbrowser

Episode = namedtuple('Episode', 'name link age')

# --------------------------------------------------------------------------- #

def parse_args(args):
    if len(args) < 2:
        print "Error: Missing arguments"
        exit()

    # if last argument is question mark, show list of eps
    if args[-1] == '?':
        searchterm = ' '.join(args[1:-1])
        epnumber = None
    elif args[-1][-1:] == '?':
        searchterm = ' '.join(args[1:])[:-1]
        epnumber = None
    # otherwise, grab most recent
    else:
        searchterm = ' '.join(args[1:])
        epnumber = 0

    return searchterm, epnumber

# --------------------------------------------------------------------------- #

def get_episodes(searchterm):
    url = 'https://eztv.it/search/'
    payload = {'SearchString': '',
               'SearchString1': searchterm,
               'search': 'Search'}
    req = requests.post(url, data=payload, timeout=5, verify=False)
    soup = BeautifulSoup(req.content, 'html.parser')

    hits = soup.findAll('a', attrs={'class': 'epinfo'})
    magnets = soup.findAll('a', attrs={'class': 'magnet'})
    released = soup.findAll('tr', attrs={'class': 'forum_header_border', 'name': 'hover'})

    # zip into a list of tuples, one tuple for each episode (name, magnet link, age)
    zipped = zip([h.text for h in hits],
                 [m['href'] for m in magnets],
                 [list(r.children)[7].text for r in released if len(list(r.children)) > 7])

    episodes = [Episode(z[0], z[1], z[2]) for z in zipped]
    return episodes

# --------------------------------------------------------------------------- #

def show_list(episodes):
    print "Select episode to download:"
    list_length = 15
    max_width = max(len(ep.name) for ep in episodes[:list_length])
    for index, ep in enumerate(episodes[:list_length]):
        print "%2d. %s %s" % (index+1,
                              ep.name[:max_width].ljust(max_width+2),
                              ep.age.ljust(9))
    inp = raw_input()
    if not str.isdigit(inp):
        return None
    epnumber = int(inp)-1
    if epnumber < 1 or epnumber > list_length:
        return None
    return epnumber

# --------------------------------------------------------------------------- #

def match_all(searchstring, epname):
    for word in searchstring.split():
        if word.lower() not in epname.lower():
            return False
    return True

# --------------------------------------------------------------------------- #

def main():
    searchterm, epnumber = parse_args(sys.argv)
    episodes = get_episodes(searchterm)

    # filter out results which dont contain all search terms
    episodes = [ep for ep in episodes if match_all(searchterm, ep.name)]

    if len(episodes) == 0:
        print "No hits."
        return

    if epnumber is None:
        epnumber = show_list(episodes)

    if epnumber is not None:
        print "Opening magnetic link for %s" % episodes[epnumber].name
        webbrowser.open_new_tab( episodes[epnumber].link )

# --------------------------------------------------------------------------- #

if __name__ == '__main__':
    main()
