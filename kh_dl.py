import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

#used to print images in the terminal
from imgcat import imgcat
from urllib import request as ulrequest
import numpy as np
import PIL.Image as Image

#glob var to prevent duplicate downloads
global downloaded_files 
downloaded_files = set()

#fnc to download a single song
def download_song(song_page_url):
    """
    This function will download a single song from a song page's URL
    Args : 
        song_page_url (str) : URL of the song page
    Return :
        None
    """
    
    if song_page_url in downloaded_files:
        return

    song_page_response = requests.get(song_page_url, headers=headers)
    song_page_response.encoding = song_page_response.apparent_encoding
    song_page_soup = BeautifulSoup(song_page_response.text, 'html.parser')
    flac_link = song_page_soup.find('a', href=lambda href: href and href.endswith('.flac'))

    if flac_link is not None:
        flac_url = urllib.parse.urljoin(song_page_url, flac_link['href'])
        filename = os.path.join(os.getcwd(), os.path.basename(flac_url))

        # Create a tqdm object for this download
        response = requests.get(flac_url, headers=headers, stream=True)

        # Download and update tqdm object
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

        downloaded_files.add(song_page_url)
    return None

def display_image(url, max_size=(300, 300)):
    """
    Display an image in the terminal 
    Args :
        url (str) : URL of the image
        max_size (tuple) : max size of the image to display
    Return :
        None
    """
    img = Image.open(ulrequest.urlopen(url))
    if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
        img.thumbnail(max_size)
    imgcat(np.asarray(img))
    return None

def download_image_from_url(image_url):
    """
    Download an image from a URL and display it in the terminal
    Args : 
        url (str) : URL of the image
    Return :
        None
    """
    display_image(image_url,max_size=(300, 300))

    image_response = requests.get(image_url, headers=headers)
    image_path = os.path.join(os.getcwd(), os.path.basename(image_url))
    with open(image_path, 'wb') as f:
        f.write(image_response.content)
    #imgcat(np.asarray(Image.open(ulrequest.urlopen(image_url))))
    os.system('cls' if os.name == 'nt' else 'clear')
    return None

### DOWNLOAD SONGS ###
#set the number of concurrent downloads
rolling_limit = int(input("Enter the rolling limit for concurrent downloads: "))
#set the url to download
url = input("Enter khinsider link to download : \n")
#url = "https://downloads.khinsider.com/game-soundtracks/album/ace-combat-zero-the-belkan-war"
#which User-Agent to use
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

#get the url webpage
response = requests.get(url, headers=headers)
#parse w/ BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')
#look of all the links in the page
soup_links = soup.find_all('a', href=True)
#look at all the link to ".mp3", they actually are links to .html pages
song_links = [link for link in soup_links if link['href'].endswith('.mp3')]

#because the .mp3 links and flac links actually are the same, we only keep one of the two
song_links = list(set(song_links))
#use a comprehension list to convert the links 
song_links = [urllib.parse.urljoin(url, link['href']) for link in song_links]
song_links = set(song_links)
#sort the set by a alphabetical order
song_links = sorted(song_links)
with ThreadPoolExecutor(max_workers=rolling_limit) as executor:
    list(tqdm(executor.map(download_song, song_links), total=len(song_links), desc="Downloading songs"))

### GET IMAGES ###
#search for jpg and png images
image_links = [link for link in soup_links if any(link['href'].endswith(ext) for ext in ['.jpg', '.png'])]
#retrieve the href links
image_links = [urllib.parse.urljoin(url, link['href']) for link in image_links]
#remove duplicates (if any)
image_links = list(set(image_links))
for image_url in image_links:
    #print the image url 
    print(image_url, "\n")
    #download the image & display it in the terminal
    download_image_from_url(image_url)

### DECODE FILENAMES ###
"""
For the flac files or the images, the filenames are encoded for the web, 
so we need to decode them to get the original filenames
"""
directory = os.getcwd( )
for filename in os.listdir(directory):
    #if the filename contains '%20' (space), rename the file
    if '%20' in filename:
        #decode the filename
        decoded_filename = urllib.parse.unquote(filename)
        #rename the file
        os.rename(os.path.join(directory, filename), os.path.join(directory, decoded_filename))

