from bs4 import BeautifulSoup
import requests
import os
import ast
from urllib.parse import urljoin, urlparse
import argparse
import sys
import json
from datetime import datetime
import html
from tqdm import tqdm


URLBASE = 'https://files02.tokybook.com/audio/'  # file source directory

class AudioBook:
    def __init__(self, title, tags, tracklist, location, properties, track_properties=None):
        self.title = title
        self.tags = tags
        self.tracklist = tracklist
        self.location = location
        self.properties = properties
        self.trackProperties = track_properties
            
    def save_properties(self):
        self.properties["tags"] = self.tags
        self.properties["track_properties"] = self.trackProperties
        self.properties["save_timestamp"] = str(datetime.now())
        with open(os.path.join(self.location, 'properties.json'), 'w', encoding='utf-8') as f:
            json.dump(self.properties, f, ensure_ascii=False, indent=4)


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
    soup = parse_url(inputs.book_url, inputs.output)
    book = get_audiobook(soup, inputs.output)
    download_audiobook(book)
    
    book.save_properties()
    
    print("-------------------------------")
    print("Audiobook Grabbed Successfully!")
    print("-------------------------------")

        
def download_audiobook(book):
    # loop through the tracks
    track_props = []
    
    progbar = tqdm(book.tracklist, position=0)
    for track in progbar:
    # for track in tracklist:
        if not track['name'] == 'welcome':  # Skip the welcome track
            track_title = track['chapter_link_dropbox']
            progbar.set_description("Downloading: {}".format(book.title))
            # Clean the URL, maybe use URLENCODE later
            # pg = urljoin(URLBASE, track_title)
            pg = urljoin(URLBASE, track_title.replace('\\', ''))
            track_props.append(
                {"track_number": track['track'], "track_name": track['name'], "track_duration": track['duration']})
            download_file(pg, book.location , track['name'])
    progbar.close()
    print("\nDownload Complete!\n")
    book.trackProperties = track_props
    # create and save the properties file to record the properties of the downloaded audio book.
    # book.save_properties(book)


def get_audiobook(soup, outpath):
        # Get the book properties from the ld+json section of the page since it is structured data.
    book_props = json.loads(
        "".join(soup.find("script", {"type": "application/ld+json"}).contents))

    # Get the book title from the book props. This should be a consistent way to get the book title.
    book_title = get_booktitle(book_props)
    print("Book Title: %s" % book_title)


    # Pull the tags for the book. These could be good for searching later.
    print("Tags: %s" % soup.find_all("span", {"class": "tags-links"})[0].get_text().strip()[5:])
    tags = soup.find_all(
        "span", {"class": "tags-links"})[0].get_text().strip()[5:].split(", ")
    
    # Get the outputFolder - makes the folder, if the default exists, it will increment
    # a number at the end so nothing is written over.
    outputFolder = get_outputfolder(outpath, book_title)
    
    
    res = soup.find_all('script')
    # There are a lot of 'script' tags in the page. Loop through them and find the one
    # with the "tracks" list.
    
    residx = 0
    for idx, script in enumerate(res):
        if "tracks = [" in str(script):
            # print("Index is: {}.".format(idx))
            residx = idx

    trackscript = res[residx]  # get the 'script' tag with the tracks list
    
    # get the string index starting the list
    trackidx = trackscript.contents[0].find('tracks = [')+9
    end = trackscript.contents[0].find(
        ']', trackidx)+1  # find the end of the list
    
    jsonstring = trackscript.contents[0][trackidx:end].replace(
        '\\n', '')  # get that string of the list

    # convert the string of the list to a real list.
    jsonstring = jsonstring.replace('\\','')
    tracklist = ast.literal_eval(jsonstring)
    return AudioBook(title=book_title, tags=tags, tracklist=tracklist,location=outputFolder, properties=book_props)


# Parse a particular URL and send files to the outpath.
def parse_url(bookURL, outpath):

    # Make sure that the domain passed in is one that we can read. If not, end things.
    domain = urlparse(bookURL).netloc
    if not domain == 'tokybook.com':
        print("Please enter a tokybook URL!")
        return

    # Get the URL page and then parse with BS4
    page = requests.get(bookURL)
    soup = BeautifulSoup(page.content, 'html.parser')

    return soup


# def save_properties(book):
#     # Add some more information to the properties that are found on the page.
#     book_props["tags"] = tags
#     book_props["track_properties"] = track_props
#     book_props["save_timestamp"] = str(datetime.now())
#     with open(os.path.join(outputFolder, 'properties.json'), 'w', encoding='utf-8') as f:
#         json.dump(book_props, f, ensure_ascii=False, indent=4)


def get_outputfolder(outpath, dirTitle="audio-", x=0):
    # This should be updated to by a better parse-able folder. Compatible with other services....
    folderpath = os.path.join(
        outpath, (dirTitle + (' ' + str(x) if x != 0 else '')).strip())
    if not os.path.exists(folderpath):
        # If it doesn't exist, make the directory
        os.mkdir(folderpath)
        print("Output Path: {}".format(folderpath))
        return folderpath
    else:
        # If it does exist, try again but increase the number at the end.
        return get_outputfolder(outpath, dirTitle, x+1)


def get_booktitle(book_props):
    # parse through the book properties to get the book title.
    # print("Parsing....")
    for props in book_props['@graph']:
        if props['@type'] == "BreadcrumbList":
            crumblist = []
            for prop in props['itemListElement']:
                crumblist.append(prop['item']['name'])
            
            # There are two names in crumblist, [0] = 'Home', [1] = Title - they are 'HTML Safe'
            book_title = html.unescape(crumblist[1])
            # print(book_title)
    return book_title


def download_file(url, outdir, name):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        file_bytes = int(r.headers.get("content-length",0))
        r.raise_for_status()
        with tqdm.wrapattr(open(os.path.join(outdir, local_filename), 'wb'), 'write',
                           miniters=1, desc="Downloading "+ name, total=file_bytes, position=1) as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
    return local_filename


if __name__ == "__main__":
    main()
