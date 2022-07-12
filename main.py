from bs4 import BeautifulSoup
import requests
import subprocess
import time
import os

page = requests.get('https://tokybook.com/the-warden-and-the-wolf-king/') #replace with url from browser bar
urlBase = 'https://files02.tokybook.com/audio/' #file source directory
#check to see if source save file exists
if os.path.exists("d:\\wget\\save.txt"):
    os.remove('d:\\wget\\save.txt')
#downloads webpage source file for parsing
with open('d:\wget\save.txt', 'wb+') as f:
    f.write(page.content)

with open('d:\\wget\\save.txt', 'r+') as f:
    #check for welcome mp3 and skips
    for line in f:
        if '<title>' in line:
            dirTitle = line[17:-41] #pulls title of the webpage for creating local directory for downloads
            if " " in dirTitle:
                dirTitle = dirTitle.replace(" ", "_")
        if ('                        "chapter_link_dropbox": "https://file.tokybook.com/upload/welcome-you-to-tokybook.mp3",') in line:
#             print('passing')
            pass
        else:
            #cutting out leading and ending line information not needed for parsing
            if 'chapter_link_dropbox' in line:
                new = line[45:-3] #45 characters from the front, 3 characters from the back
                if ' ' in new: #looking for spaces in filename and replacing with web friendly spacing
                    newnew = new.replace(" ", "%20")
                    newnewnew = (urlBase + newnew)
                    if '\\' in newnewnew: #removing \ that might cause errors in file names. \ doesn't always error
                        final = newnewnew.replace('\\', "") #final mp3 file name
#                         print(final)
                        print(dirTitle)
                        cwd = os.getcwd() #
                        os.chdir('d:\\wget\\') #directory with wget.exe
                        #calls wget with 15 second timeout, makes directory based off dirTitle
                        subprocess.Popen('wget.exe --timeout=15 --directory-prefix=' + dirTitle + " " + final)
                        time.sleep(3)
                    else:
                        print('error')
                else: #catch for when there are no spaces in var new, only one case found. same work as above
                    if '\\' in new:
                        removal = new.replace('\\', "")
                        final = (urlBase + removal)
                        print(final)
                        cwd = os.getcwd()
                        os.chdir('d:\\wget\\')
                        subprocess.Popen('wget.exe --timeout=15 --directory-prefix=' + dirTitle + " " + final)
                        time.sleep(3)