from bs4 import BeautifulSoup
import requests
import os
import ast
from urllib.parse import urljoin

# implement argparse to receive the output location
path = os.getcwd()
# implement argparse to receive the page location
page = requests.get('https://tokybook.com/the-warden-and-the-wolf-king/')

URLBASE = 'https://files02.tokybook.com/audio/'  # file source directory


def main():
    soup = BeautifulSoup(page.content, 'html.parser')

    dirTitle = soup.find_all('h1')[0].get_text().strip()
    # print(dirTitle)

    outputFolder = os.path.join(path, dirTitle)
    os.mkdir(outputFolder)

    res = soup.find_all('script')[19]

    # print(res)

    trackidx = res.contents[0].find('tracks = [')+9
    end = res.contents[0].find(']', trackidx)+1
    jsonstring = res.contents[0][trackidx:end].replace('\\n', '')

    tracklist = ast.literal_eval(jsonstring)

    for track in tracklist:
        if not track['name'] == 'welcome':
            dirtitle = track['chapter_link_dropbox']
            pg = urljoin(URLBASE, dirtitle.replace('\\', ''))
            download_file(pg, outputFolder)


def download_file(url, outdir):
    # print('Downloading {}'.format(url))
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(os.path.join(outdir, local_filename), 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
    return local_filename


if __name__ == "__main__":
    main()
