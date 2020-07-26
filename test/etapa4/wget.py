from pathlib import Path
import requests
"""
Downloads file from internet to director with url endpoint
name by default (like !wget). Can specify optional keyword arguments:

	`filename`: Filename to be saved as. String.
	`dir`: Directory to save to. Can be absolute or relative
	`prnt`: Print file contents. Default False.
"""
def wget(url, **args):
    filename = args["name"] if "name" in args else url[url.rfind('/') + 1::]
    dir = args["dir"] + "/" if "dir" in args else ""
    Path(dir).mkdir(parents=True, exist_ok=True)
    showContents = args["prnt"] if "prnt" in args else False
    try:
      r = requests.get(url, allow_redirects=True)
    except:
      raise ValueError('Error retrieving ' + url)
    with open(dir+filename, 'wb') as f:
        f.write(r.content)
    if showContents:
    	print(r.content)