Bulk download audio files from tokybook.com<br>
  Writen with Python 3.9<br>
    Required modules: bs4, requests, subprocess, time, os<br>
  Creates subdirectory for files based off webpage title.<br>
    -Sometimes not great because there are no standard naming conventions used on the site.<br>
    <br>
How to use:<br><br>

  -Change path of wget to your own.<br>
    All files will download into the wget working directory.<br>
    Stored copy of webpage source for parsing, along with directories for downloads.<br>
  -Copy/paste the page url into the 'page = requests.get()'<br>
  -Run script<br>
