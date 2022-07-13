from bs4 import BeautifulSoup
import requests
import os
import ast
from urllib.parse import urljoin, urlparse
import argparse
import sys
import json
from datetime import datetime

URLBASE = 'https://files02.tokybook.com/audio/'  # file source directory


# Parse the arguments passed via the command line.
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

# Main loop.


def main():
    inputs = parse_args()
    if inputs.file:
        print("Not yet implemented. Please check for an update and try again later.")
        return
    parse_url(inputs.book_url, inputs.output)

# Parse a particular URL and send files to the outpath.


def parse_url(bookURL, outpath):

    # Make sure that the domain passed in is one that we can read. If not, end things.
    domain = urlparse(bookURL).netloc
    if not domain == 'tokybook.com':
        print("Please entere a tokybook URL!")
        return

    # Get the URL page and then parse with BS4
    page = requests.get(bookURL)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get the book properties from the ld+json section of the page since it is structured data.
    book_props = json.loads(
        "".join(soup.find("script", {"type": "application/ld+json"}).contents))

    # Get the book title from the book props. This should be a consistent way to get the book title.
    book_title = get_booktitle(book_props)

    # Get the outputFolder - makes the folder, if the default exists, it will increment
    # a number at the end so nothing is written over.
    outputFolder = get_outputfolder(outpath, book_title)

    # Pull the tags for the book. These could be good for searching later.
    tags = soup.find_all(
        "span", {"class": "tags-links"})[0].get_text()[5:].split(", ")

    res = soup.find_all('script')

    # There are a lot of 'script' tags in the page. Loop through them and find the one
    # with the "tracks" list.
    residx = 0
    for idx, script in enumerate(res):
        if "tracks = [" in str(script):
            print("Index is: {}.".format(idx))
            residx = idx

    trackscript = res[residx]  # get the 'script' tag with the tracks list
    # get the string index starting the list
    trackidx = trackscript.contents[0].find('tracks = [')+9
    end = trackscript.contents[0].find(
        ']', trackidx)+1  # find the end of the list
    jsonstring = trackscript.contents[0][trackidx:end].replace(
        '\\n', '')  # get that string of the list

    # convert the string of the list to a real list.
    tracklist = ast.literal_eval(jsonstring)

    # loop through the tracks
    track_props = []
    for track in tracklist:
        if not track['name'] == 'welcome':  # Skip the welcome track
            track_title = track['chapter_link_dropbox']
            # Clean the URL, maybe use URLENCODE later
            pg = urljoin(URLBASE, track_title.replace('\\', ''))
            track_props.append(
                {"track_number": track['track'], "track_name": track['name'], "track_duration": track['duration']})
            download_file(pg, outputFolder)

    # create and save the properties file to record the properties of the downloaded audio book.
    save_properties(outputFolder, book_props, tags, track_props)


def save_properties(outputFolder, book_props, tags, track_props):
    # Add some more information to the properties that are found on the page.
    book_props["tags"] = tags
    book_props["track_properties"] = track_props
    book_props["save_timestamp"] = str(datetime.now())
    with open(os.path.join(outputFolder, 'properties.json'), 'w', encoding='utf-8') as f:
        json.dump(book_props, f, ensure_ascii=False, indent=4)


def get_outputfolder(outpath, dirTitle, x=0):
    folderpath = os.path.join(
        outpath, (dirTitle + (' ' + str(x) if x != 0 else '')).strip())
    if not os.path.exists(folderpath):
        # If it doesn't exist, make the directory
        os.mkdir(folderpath)
        return folderpath
    else:
        # If it does exist, try again but increase the number at the end.
        return get_outputfolder(outpath, dirTitle, x+1)


def get_booktitle(book_props):
    # parse through the book properties to get the book title.
    for props in book_props['@graph']:
        if props['@type'] == "BlogPosting":
            book_title = props['name']
            return book_title


def download_file(url, outdir):
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
