import requests
from bs4 import BeautifulSoup
import json
from lxml import html

base_url = 'http://chinese-characters.org/pinyin'
image_url_prefix = 'http://chinese-characters.org/images'

character_url = 'http://chinese-characters.org/meaning/5/5446.html'
unavail_url = 'unavail.png'

data = dict()

def extract_data_from_character_url(character_url):
    datum = dict()
    parsed_response = BeautifulSoup(requests.get(character_url).content)
    images = [tag for tag in parsed_response.find_all('img')]
    fonts = [tag for tag in parsed_response.find_all('font') if tag.get('size') == '+2']

    images = [tag for tag in parsed_response.find_all('img') if 'http://chinese-characters.org/images/' in tag.get('src')]
    datum['simplified_image'] = [img for img in images if f'{image_url_prefix}/2simp/' in img['src']][0]
    datum['traditional_image'] = [img for img in images if f'{image_url_prefix}/1trad/' in img['src']][0]
    datum['ancient1_image'] = [img for img in images if f'{image_url_prefix}/1ancient/' in img['src']][0]
    datum['ancient2_image'] = [img for img in images if f'{image_url_prefix}/2ancient/' in img['src']][0]
    datum['archaic_images'] = [img for img in images if f'{image_url_prefix}/1archaic/' in img['src']]
    

    titles_td = parsed_response.find_all('td', background='../../images/table4-2-1.png')[0]
    parent_tr = titles_td.parent 
    tds = parent_tr.next_sibling.next_sibling.find_all('td', align='center')
    
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

    # variants
    datum['variants_link'], datum['variants_text'] = extract_links_and_text(tds[0])
    
    # phonetic
    datum['phonetic_link'], datum['phonetic_text'] = extract_links_and_text(tds[1])
    # semantic
    datum['semantic_link'], datum['semantic_text'] = extract_links_and_text(tds[2])
    # apparent
    datum['apparent_link'], datum['apparent_text'] = extract_links_and_text(tds[3])
 


    left_trs = [tr for tr in parsed_response.find_all('tr') if tr.get('align') == 'left']
    tr1 = left_trs[0]
    tr2 = left_trs[1]

    pronunciation = parsed_response.find_all('center')[-1].text.rstrip()
    definition = [tr for tr in parsed_response.find_all('tr') if tr.get('align') == 'left']
    mnemonic = parsed_response.find_all('')

    [tag for tag in parsed_response.find_all('td') if tag.get('align') == 'left']

    return datum


def main():
    parsed_response = BeautifulSoup(requests.get(base_url).content)
    letters_urls = [tag['href'] for tag in parsed_response.find_all('a') if 'pinyin' in tag['href']]
    for letter_url in letters_urls:
        parsed_response = BeautifulSoup(requests.get(letter_url).content)
        sounds_urls = [tag['href'] for tag in parsed_response.find_all('a') if 'pinyin' in tag['href']]
        for sound_url in sounds_urls:
            parsed_response = BeautifulSoup(requests.get(sound_url).content)
            characters_urls = [tag['href'] for tag in parsed_response.find_all('a') if 'meaning' in tag['href']]
            for character_url in characters_urls:
                data.append(extract_data_from_character_url(character_url))


if __name__ == '__main__':
    main()
    with open('data.json', 'w') as json_file:
        json.dump(data, json_file)