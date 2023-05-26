#!/usr/bin/env python3
import argparse, pathlib, re, requests, urllib, zipfile
from bs4 import BeautifulSoup

package_names = [
    'CTCaer/hekate',
    'Atmosphere-NX/Atmosphere',
    'HamletDuFromage/aio-switch-updater',
    'XorTroll/Goldleaf',
    'J-D-K/JKSV',
    'DarkMatterCore/nxdumptool',
    'meganukebmp/Switch_90DNS_tester',
    'suchmememanyskill/TegraExplorer',
    'tiliarou/tinfoil-1'
]

def get_package(repo):
    # Get most recent tag
    response = requests.get('https://github.com/'+repo+'/tags')
    soup = BeautifulSoup(response.text, features="html.parser")
    tag = soup.h2.contents[0].contents[0]
    
    # Get most recent package
    response = requests.get('https://github.com/'+repo+'/releases/expanded_assets/'+tag)
    soup = BeautifulSoup(response.text, features="html.parser")
    
    # Fetch URLs for download
    download_locations = [ soup.a.attrs['href'] ]
    if repo == 'Atmosphere-NX/Atmosphere': # Grab fusee.bin too
        download_locations.append(soup.find_all('a')[1]['href']) 

    return download_locations, tag

def download_package(repo):
    # Tinfoil does not support releases--hopefully this can be removed at some point
    if repo == 'tiliarou/tinfoil-1': 
        urllib.request.urlretrieve('https://github.com/'+repo+'/raw/master/tinfoil.nro',
                                       './downloads/tinfoil.nro')
        print(f'Downloading {repo} : latest')
        return
    # Download package
    download_locations, tag = get_package(repo)
    print(f'Downloading {repo} : {tag}')
    for download_location in download_locations:
        urllib.request.urlretrieve('https://github.com'+download_location,
                                    './downloads/'+re.search('[^/]+$', download_location).group())

# Delete directory contents
def rm_tree(pth):
    pth = pathlib.Path(pth)
    for child in pth.glob('*'):
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    pth.rmdir()

# Configure arg parser
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clean', action='store_true', 
                        help='delete download directory and re-download')
    parser.set_defaults(clean=False)
    args = parser.parse_args()
    return args

def create_folder_structure():
    # Create directories
    pathlib.Path('./drag-n-drop/switch/aio-switch-updater', exist_ok=True).mkdir(parents=True, exist_ok=True)
    pathlib.Path('./drag-n-drop/bootloader/payloads', exist_ok=True).mkdir(parents=True, exist_ok=True)

    # Unzip AIO Switch Updater
    with zipfile.ZipFile('./downloads/aio-switch-updater.zip', 'r') as zip_ref:
        zip_ref.extractall('./drag-n-drop')

    # Unzip Atmosphere package
    with zipfile.ZipFile('./downloads/atmosphere-1.5.4-prerelease-3cb54e2b4+hbl-2.4.3+hbmenu-3.5.1.zip', 'r') as zip_ref:
        zip_ref.extractall('./drag-n-drop')

    # Unzip hekate package
    with zipfile.ZipFile('./downloads/hekate_ctcaer_6.0.4_Nyx_1.5.3.zip', 'r') as zip_ref:
        zip_ref.extractall('./drag-n-drop')
    for f in pathlib.Path('./drag-n-drop').glob('hekate*.bin'):
        f.rename(pathlib.Path('./drag-n-drop/bootloader/payloads').joinpath(f.name))

    # Copy *.nro and *.bin files
    for f in pathlib.Path('./downloads').glob('*.nro'):
        f.rename(pathlib.Path('./drag-n-drop/switch').joinpath(f.name))
    for f in pathlib.Path('./downloads').glob('*.bin'):
        f.rename(pathlib.Path('./drag-n-drop/bootloader/payloads').joinpath(f.name))

    # Delete download folder as it is no longer needed
    rm_tree('./downloads')

def main():
    # Check for downloads folder and delete if requested
    args = parse_args()
    if args.clean:
        if pathlib.Path('./downloads').is_dir(): rm_tree('./downloads')
        if pathlib.Path('./drag-n-drop').is_dir(): rm_tree('./drag-n-drop')
    elif pathlib.Path('./downloads').is_dir() or pathlib.Path('./drag-n-drop').is_dir():
        print('You have already downloaded packages, run again with --clean if you wish to delete them.')
        return

    # Create downloads directory and download packages
    pathlib.Path('./downloads', exist_ok=True).mkdir(parents=True, exist_ok=True)
    for repo in package_names:
        download_package(repo)

    create_folder_structure()
    print('Packages downloaded and sorted.\n\n'
          'Open drag-n-drop directory and drag all of the contents to the Switch microSD card.')

if __name__ == "__main__":
    main()
