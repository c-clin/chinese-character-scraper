import requests
from bs4 import BeautifulSoup
import json
from lxml import html

base_url = 'http://chinese-characters.org/pinyin'
image_url_prefix = 'http://chinese-characters.org/images'

unavail_url = 'unavail.png'

characters_urls = set()
data = dict()

def extract_links_and_text(tag):
    links = list()
    text = list()
    for link in tag.find_all('a'):
        href = link.get('href', '')
        if unavail_url in href:
            continue
        links.append(link.get('href', ''))
        if link.find('font'):
            font = link.find('font')
            text.append(font.contents[0])
        else:
            text.append(link.contents[0])
        
    return [links,text]


def extract_data_from_character_url(character_url):
    datum = dict()
    parsed_response = BeautifulSoup(requests.get(character_url).content, features='lxml')
    images = [tag for tag in parsed_response.find_all('img')]
    fonts = [tag for tag in parsed_response.find_all('font') if tag.get('size') == '+2']

    images = [tag for tag in parsed_response.find_all('img') if 'http://chinese-characters.org/images/' in tag.get('src')]
    datum['simplified_images'] = [img.get('src') for img in images if f'{image_url_prefix}/2simp/' in img['src']]
    datum['traditional_images'] = [img.get('src') for img in images if f'{image_url_prefix}/1trad/' in img['src']]
    datum['ancient1_images'] = [img.get('src') for img in images if f'{image_url_prefix}/1ancient/' in img['src']]
    datum['ancient2_images'] = [img.get('src') for img in images if f'{image_url_prefix}/2ancient/' in img['src']]
    datum['archaic_images'] = [img.get('src') for img in images if f'{image_url_prefix}/1archaic/' in img['src']]

    titles_td = parsed_response.find_all('td', background='../../images/table4-2-1.png')[0]
    parent_tr = titles_td.parent 
    tds = parent_tr.next_sibling.next_sibling.find_all('td', align='center')

    datum['variants_link'], datum['variants_text'] = extract_links_and_text(tds[0])
    datum['phonetic_link'], datum['phonetic_text'] = extract_links_and_text(tds[1])
    datum['semantic_link'], datum['semantic_text'] = extract_links_and_text(tds[2])
    datum['apparent_link'], datum['apparent_text'] = extract_links_and_text(tds[3])

    left_trs = [tr for tr in parsed_response.find_all('tr') if tr.get('align') == 'left']
    tr_definition = left_trs[1]
    tr_mnemonic = left_trs[2]

    datum['pronunciation'] = parsed_response.find_all('center')[-1].text.rstrip().lstrip()
    datum['defintion'] = list(tr_definition.children)[-1].text.rstrip().lstrip()
    # TODO: parse links, topological sort vocab words
    datum['mnemonic'] = list(tr_mnemonic.children)[-1].text.rstrip().lstrip()

    # TODO: get character as text for lookup

    # TODO: get etymology

    return datum


def main():
    parsed_response = BeautifulSoup(requests.get(base_url).content, features='lxml')
    letters_urls = [tag['href'] for tag in parsed_response.find_all('a') if 'pinyin' in tag['href']]
    for letter_url in letters_urls:
        parsed_response = BeautifulSoup(requests.get(letter_url).content, features='lxml')
        sounds_urls = [tag['href'] for tag in parsed_response.find_all('a') if 'pinyin' in tag['href']]
        for sound_url in sounds_urls:
            parsed_response = BeautifulSoup(requests.get(sound_url).content, features='lxml')
            characters_urls |= {tag['href'] for tag in parsed_response.find_all('a') if 'meaning' in tag['href']}
    
    for character_url in characters_urls:
        print(f'character_url = {character_url}')
        try:
            data[character_url] = extract_data_from_character_url(character_url)
        except Exception:
            pass


if __name__ == '__main__':
    main()
    with open('data.json', 'w') as json_file:
        json.dump(data, json_file)
