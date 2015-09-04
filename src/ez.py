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
import sys, requests, webbrowser, re, traceback, time
# from operator import attrgetter

# disallow same episode listed multiple times
NO_DUPLICATES = False

Episode = namedtuple('Episode', 'name link age')

# --------------------------------------------------------------------------- #

def parse_args(args):
    if len(args) < 2:
        print "Error: Missing arguments"

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

def filter_dupes(episodes):
    if len(episodes) == 0:
        return

    # if first episode name doesn't contain S00E00, abort
    check_naming = re.search('S\d\dE\d\d', episodes[0].name)
    if check_naming == None:
        return episodes

    # set to check against duplicate episode numbers
    epset = set()

    def is_dupe(name):
        hit = re.search('S\d\dE\d\d', name)
        if hit != None:
            ep = name[hit.start():hit.start()+6]
            if ep in epset:
                return True
            else:
                epset.add(ep)
                return False

    # filter out dupes
    episodes = [ep for ep in episodes if not is_dupe(ep.name)]

    # sort the list (may break most recent on top)
    # episodes = sorted(episodes, key=attrgetter('name'), reverse=True)
    return episodes

# --------------------------------------------------------------------------- #

def get_episodes(searchterm):
    try:
        # start_time = time.time()
        # url = 'https://eztv.it/search/'
        url = 'https://eztv.ch/search/'
        # url = 'https://eztv-proxy.net/search/'
        # url = 'http://eztv.bitproxy.eu/'
        payload = {'SearchString': '',
                   'SearchString1': searchterm,
                   'search': 'Search'}
        req = requests.post(url, data=payload, timeout=60, verify=False)
        soup = BeautifulSoup(req.content, 'html.parser')

        hits = soup.findAll('a', attrs={'class': 'epinfo'})
        magnets = soup.findAll('a', attrs={'class': 'magnet'})
        released = soup.findAll('tr', attrs={'class': 'forum_header_border', 'name': 'hover'})

        # zip into a list of tuples, one tuple for each episode (name, magnet link, age)
        zipped = zip([h.text for h in hits],
                     [m['href'] for m in magnets],
                     [list(r.children)[7].text for r in released if len(list(r.children)) > 7])

        episodes = [Episode(z[0], z[1], z[2]) for z in zipped]
        # print "GET took %.2f sec" % (time.time()-start_time)
        return episodes
    except:
        print traceback.format_exc()
        # print sys.exc_info()[0]
        raw_input()
        # print "Connection failed"
        exit()

# --------------------------------------------------------------------------- #

def show_list_selection(episodes):
    print "Select episode to download:"
    list_length = 15
    max_width = max(len(ep.name) for ep in episodes[:list_length])
    for index, ep in enumerate(episodes[:list_length]):
        print "%2d. %s %s" % (index+1,
                              ep.name[:max_width].ljust(max_width+2),
                              ep.age.ljust(9))
    try:
        inp = raw_input()
    except KeyboardInterrupt:
        exit()
    if not str.isdigit(inp):
        return None
    epnumber = int(inp)-1
    if epnumber < 0 or epnumber > list_length-1:
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
    sys.argv = ['', 'maher?']
    searchterm, epnumber = parse_args(sys.argv)
    episodes = get_episodes(searchterm)

    # filter out results which dont contain all search terms
    episodes = [ep for ep in episodes if match_all(searchterm, ep.name)]

    if NO_DUPLICATES:
        episodes = filter_dupes(episodes)

    if len(episodes) == 0 or not episodes:
        print "No hits."
        return

    if epnumber is None:
        epnumber = show_list_selection(episodes)

    if epnumber is not None:
        print "Opening magnetic link for %s" % episodes[epnumber].name
        webbrowser.open_new_tab( episodes[epnumber].link )

# --------------------------------------------------------------------------- #

if __name__ == '__main__':
    main()
