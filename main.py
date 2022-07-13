from bs4 import BeautifulSoup
import requests
import os
import ast
from urllib.parse import urljoin, urlparse
import argparse
import sys
import json

# implement argparse to receive the output location
# path = os.getcwd()
# implement argparse to receive the page location
# page = requests.get('https://tokybook.com/the-warden-and-the-wolf-king/')

URLBASE = 'https://files02.tokybook.com/audio/'  # file source directory


def parse_args():
    parser = argparse.ArgumentParser(
        description="This program downloads all the tracks from the given URL.")
    parser.add_argument(
        '--book-url', '-b', help="Enter the URL for the book.", type=str, default='')
    parser.add_argument(
        '--output', '-o', help="Location where folder for the book is created." +
        "Defaults to current directory.",
        type=str, default=os.getcwd()
    )
    parser.add_argument(
        '--file', '-f', help="File with list of links.", type=str, default='')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if not args.book_url:
        print("Please enter a URL for the Book!")
        parser.print_help(sys.stderr)
        sys.exit(1)

    return args


def main():
    inputs = parse_args()
    parse_url(inputs.book_url, inputs.output)


def parse_url(bookURL, outpath):
    domain = urlparse(bookURL).netloc
    if not domain == 'tokybook.com':
        print("Please entere a tokybook URL!")
        return

    page = requests.get(bookURL)

    soup = BeautifulSoup(page.content, 'html.parser')

    # dirTitle = soup.find_all('h1')[0].get_text().strip()
    # print(dirTitle)

    book_props = json.loads(
        "".join(soup.find("script", {"type": "application/ld+json"}).contents))

    book_title = get_booktitle(book_props)

    outputFolder = get_outputfolder(outpath, book_title)

    with open(os.path.join(outputFolder, 'properties.json'), 'w', encoding='utf-8') as f:
        json.dump(book_props, f, ensure_ascii=False, indent=4)

    res = soup.find_all('script')

    residx = 0
    for idx, script in enumerate(res):
        if "tracks = [" in str(script):
            print("Index is: {}.".format(idx))
            residx = idx

    trackscript = res[residx]
    trackidx = trackscript.contents[0].find('tracks = [')+9
    end = trackscript.contents[0].find(']', trackidx)+1
    jsonstring = trackscript.contents[0][trackidx:end].replace('\\n', '')

    tracklist = ast.literal_eval(jsonstring)

    for track in tracklist:
        if not track['name'] == 'welcome':
            track_title = track['chapter_link_dropbox']
            pg = urljoin(URLBASE, track_title.replace('\\', ''))
            download_file(pg, outputFolder)


def get_outputfolder(outpath, dirTitle, x=0):
    folderpath = os.path.join(
        outpath, (dirTitle + (' ' + str(x) if x != 0 else '')).strip())
    if not os.path.exists(folderpath):
        os.mkdir(folderpath)
        return folderpath
    else:
        return get_outputfolder(outpath, dirTitle, x+1)


def get_booktitle(book_props):
    for props in book_props['@graph']:
        if props['@type'] == "BlogPosting":
            book_title = props['name']
            return book_title


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
