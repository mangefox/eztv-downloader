# eztv-downloader
Get tv episodes from eztv.it through command line.

Uses magnetic links so you will need to have them associated with a torrent client.

### Dependencies
Requires _requests_ and _BeautifulSoup4_ (`pip install requests bs4`)

Make sure your .py association passes arguments (e.g. `"C:\Python36\python.exe" "%1" %*`)

### Example usage
 ` ez.py family guy` will download most recent family guy ep
  
  `ez.py marco polo s01e10` will download this specific episode
  
  `ez.py top gear?` will show list of most recent top gear eps
  
  `ez.py the wire s05?` will show list of season 5 episodes of the wire
  
  
![Example](http://i.imgur.com/2hLlFIu.png)
