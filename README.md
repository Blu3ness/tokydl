Bulk download audio files from tokybook.com
  Writen with Python 3.9
    Required modules: bs4, requests, subprocess, time, os
  Creates subdirectory for files based off webpage title.
    -Sometimes not great because there are no standard naming conventions used on the site.
    
How to use:

  -Change path of wget to your own.
    All files will download into the wget working directory.
    Stored copy of webpage source for parsing, along with directories for downloads.
  -Copy/paste the page url into the 'page = requests.get()'
  -Run script
