import click
import requests
import json
# import tomd Soon™
import sys
from bs4 import BeautifulSoup


def get_novel_links(novel):
    print('Gathering List of chapter links..')
    novel_name = novel.split('/')[-1].replace('-', ' ').capitalize()
    res = requests.get(novel)
    soup = BeautifulSoup(res.text, 'html.parser')
    link_col = []
    link_li = soup.find('ul', {'class': 'chapter-chs'}).find_all('li')
    for li in link_li:
        link_col.append('/'.join(li.find('a').get('href').split('/')[-2:]))

    novel_json = {}
    novel_json['base_link'] = novel
    novel_json['chapter_list'] = link_col
    novel_json['chapters'] = []
    with open(f'{novel_name}.json', 'w') as outfile:
        json.dump(novel_json, outfile, indent=4)

    return link_col

def update_progress(progress, status):
    if progress <= 100:
        sys.stdout.write(f"\r[{progress}%] Downloading {status}"),
    elif progress >= 100:
        sys.stdout.write('\n Completed!')
    sys.stdout.flush()


def download_chapter(novel):
    novel_name = novel.split('/')[-1].replace('-', ' ').capitalize()
    i = 0
    with open(f'{novel_name}.json') as json_file:
        novel_data = json.load(json_file)
        l = len(novel_data['chapter_list'])
        for chapter in novel_data['chapter_list']:
            i = i + 1
            chapter_name = chapter.split('/')[-1].replace('-', ' ').capitalize()
            res = requests.get('/'.join([novel_data['base_link'], chapter]))
            soup = BeautifulSoup(res.text, 'html.parser')
            soup.find('div', {'class': 'chapter-content3'}).find('div', {'class': 'desc'}).find(id='growfoodsmart').decompose()
            [s.decompose() for s in soup(['script', 'iframe', 'center'])]
            novel_data['chapters'].append({chapter_name: soup.find('div', {'class': 'chapter-content3'}).find('div', {'class': 'desc'}).getText()})
            update_progress(round((100 * (i + 1) ) / l), chapter_name)
    with open(f'{novel_name}.json', 'w') as outfile:
        json.dump(novel_data, outfile, indent=4)
    return

@click.group()
def main():
    """
    Little script I made to save Novels on my laptop so I can read them later.
    Run: main.py <novel link, ex: https://www.readlightnovel.org/example-novel-link>
    Use the flag -l to retrieve all the links, -d to download all the chapters and put them on a json.
    """

@main.command()
@click.argument('novel')
@click.option(
    '--links', '-l',
    is_flag=True,
    help='Get the Novel chapter links',
)
@click.option(
    '--download', '-d',
    is_flag=True,
    help='Download the chapters into the json',
)
def novel(novel, links, download):
    """
    Retrieve and save the novel links.
    """
    novel_name = novel.split('/')[-1].replace('-', ' ').capitalize()
    if links: link_list = get_novel_links(novel)
    if download: download_chapter(novel)

if __name__ == '__main__':
    main()
