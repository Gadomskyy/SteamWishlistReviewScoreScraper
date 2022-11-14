import requests
import json
import re
import bs4
import csv
from time import sleep


def get_html(url):
    #bez tych headersów robi się TooManyRedirects Error
    s = requests.Session()
    s.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
    response = s.get(url)
    #sleep zeby nie bylo za duzo requestow naraz
    sleep(0.3)
    if not response.ok:
        print(f'{response.status_code}, URL: {url} Error')
    return response.text


def json_parse(json_file):
    parsed_json = json.loads(json_file)
    temporary_list = []
    #znalezc subkey 'name', tam jest nazwa gry
    #primary key rozni sie dla kazdej gry wiec trzeba po tym iterowac
    for key in parsed_json.keys():
        temporary_list.append(parsed_json[key]['name'].lower())
    return temporary_list


def name_adjst(name_list):
    new_list = []
    for name in name_list:
        #usuwanie znakow specjalnych ktorych nie bedzie w url takich jak (,: itp
        removed_chars_str_1 = re.sub(r"[^a-zA-Z0-9']+", ' ', name)
        #czy da sie to zrobic w jednym kroku?
        removed_chars_str_2 = re.sub(r"[']+", '', removed_chars_str_1)
        #polaczenie oddzielnych slow myslnikiem bo tak jest w URLu
        new_name = '-'.join(removed_chars_str_2.split(' '))
        #jesli special character byl na koncu to dodaje sie tam myslnik, trzeba go usunac
        if new_name[-1] == '-':
            new_name = new_name[:-1]
        new_list.append(new_name)
    return new_list


def metacritic_link_generator(game_name):
    return f'https://www.metacritic.com/game/pc/{game_name}'


def metacritic_info_get(game_url):
    info_list = []
    soup = bs4.BeautifulSoup(get_html(game_url), 'html.parser')
    try:
        #Critic Score
        criticScore = soup.find('div', class_=lambda value: value and value.startswith("metascore_w x")).text
        info_list.append(criticScore)
    except AttributeError:  # URL problem lub brak ocen na stronie
        criticScore = 'N/A'
        info_list.append(criticScore)
        # User Score
    try:
        userScore = soup.find('div', class_=lambda value: value and value.startswith("metascore_w user")).text
        info_list.append(userScore)
    except AttributeError:  #URL problem lub brak ocen na stronie
        userScore = 'N/A'
        info_list.append(userScore)
    return info_list


def main():
    url = 'https://store.steampowered.com/wishlist/profiles/76561198031692699/wishlistdata/?p=0&v='
    get_html(url)
    i = 0
    name_list = []
    while True:
        url = f'https://store.steampowered.com/wishlist/profiles/76561198031692699/wishlistdata/?p={i}&v='
        if len(requests.get(url).text) > 2:
            name_list.extend(json_parse(get_html(url)))
            i += 1
        else:
            break
    all_links = []
    for game_name in name_adjst(name_list):
        all_links.append(metacritic_link_generator(game_name))
    game_counter = 0
    with open('steamWishlistReviewScores.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        header = ['Game name', 'Critic Score', 'User Score']
        writer.writerow(header)
        for game_link in all_links:
            all_info = []
            all_info.append(name_list[game_counter])
            game_information = metacritic_info_get(game_link)
            all_info.extend(game_information)
            writer.writerow(all_info)
            game_counter += 1


if __name__ == "__main__":
    main()
