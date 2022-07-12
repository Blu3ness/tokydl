from bs4 import BeautifulSoup
import requests
import subprocess
import time
import os

page = requests.get('https://tokybook.com/before-the-storm-audiobook/')
urlBase = 'https://files02.tokybook.com/audio/'

if os.path.exists("d:\\wget\\save.txt"):
    os.remove('d:\\wget\\save.txt')

with open('d:\wget\save.txt', 'wb+') as f:
    f.write(page.content)

with open('d:\\wget\\save.txt', 'r+') as f:
    #check for welcome mp3 and skips
    for line in f:
        if '<title>' in line:
            dirTitle = line[17:-41]
            if " " in dirTitle:
                dirTitle = dirTitle.replace(" ", "_")
        if ('                        "chapter_link_dropbox": "https://file.tokybook.com/upload/welcome-you-to-tokybook.mp3",') in line:
#             print('passing')
            pass
        else:
            if 'chapter_link_dropbox' in line:
                new = line[45:-3]
                if ' ' in new:
                    newnew = new.replace(" ", "%20")
                    newnewnew = (urlBase + newnew)
                    if '\\' in newnewnew:
                        final = newnewnew.replace('\\', "")
#                         print(final)
                        print(dirTitle)
                        cwd = os.getcwd()
                        os.chdir('d:\\wget\\')
                        subprocess.Popen('wget.exe --timeout=15 --directory-prefix=' + dirTitle + " " + final)
                        time.sleep(3)
                    else:
                        print('error')
                else:
                    if '\\' in new:
                        removal = new.replace('\\', "")
                        final = (urlBase + removal)
                        print(final)
                        cwd = os.getcwd()
                        os.chdir('d:\\wget\\')
                        subprocess.Popen('wget.exe --timeout=15 --directory-prefix=' + dirTitle + " " + final)
                        time.sleep(3)