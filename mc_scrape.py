"""
SOURCE1: https://realpython.com/beautiful-soup-web-scraper-python/
SOURCE2: https://towardsdatascience.com/web-scraping-metacritic-reviews-using-beautifulsoup-63801bbe200e
Apps Script web scraper: https://medium.com/@interdigitizer/scrape-and-save-data-to-google-sheets-with-apps-script-7e3c0ccec96b
BeautifulSoup scraper: https://pypi.org/project/beautifulsoup4/
BautifulSoup docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
"""

# Getting URL and Scraping
import requests
from bs4 import BeautifulSoup
import re
import string
import numpy as np
import warnings

# BAD PRACTICE. Just for nice output. IAFOSLFJAA:SF:AFJLAFA:SFJLF:LSAJaslfkFKASJ:LJFLJFASLFKLA:JSF
warnings.filterwarnings("ignore")

# Define Vars
base_url = 'https://www.metacritic.com/game/'  # Base URL
user_agent = {'User-agent': 'Mozilla/5.0'}
platforms_test = ['playstation-4', 'xbox-one',
                  'switch', 'stadia',  'wii-u', 'playstation-3', 'xbox-360', 'pc', 'xbox', 'wii',  'playstation-2', 'nintendo-64', 'gamecube', 'playstation', '3ds', 'psp', 'game-boy-advance', 'ds', 'ios', 'playstation-vita']
printout = True

debug_mode = False


# Define Functions


def isNumber(num):
    try:
        float(num)
        return True
    except:
        return False


def calcAverage(array):
    try:
        return np.average([float(i) for i in array if isNumber(i)])
    except:
        return 'N/A'


def parseTitle(title):
    # Parse human-readable title to URL searchable title.
    # Convert space to dash, remove symbols, lowercase
    parsed = title.translate(title.maketrans(' ', '-', '!@:#;\'')).lower()
    return parsed


def getGameURL(title):
    # see if the game exists on PC, otherwise cycle through other platforms until we get an OK
    for plat in platforms_test:
        request_url = base_url+plat+'/'+parseTitle(title)
        r = requests.get(request_url, headers=user_agent)

        if (r.status_code == 200):
            break

    return request_url, [plat]


def getValidGameURLs(title):
 # See what platforms the game exists on, and append a 'valid URLs' list.
    game_urls = []
    platforms = []

    for plat in platforms_test:
        request_url = base_url+plat+'/'+parseTitle(title)
        r = requests.get(request_url, headers=user_agent)

        if (r.status_code == 200):
            game_urls.append(request_url)
            platforms.append(plat)

    if not game_urls:
        print('No game entries found, you simpleton.')
        exit()

    return game_urls, platforms


def listToString(str_list):
    str_format = ' '
    length = len(str_list)
    if length > 1:
        for x in range(length):
            str_format += str_list[x]
            if ((length > 2) & (x < (length-2))):
                str_format += ', '
            elif (x == (length-2)):
                str_format += ' & ' + str_list[x+1]
                break

    else:
        str_format += str_list[0]

    return str_format


def isVowel(ch):
    if(ch == 'a' or ch == 'e' or ch == 'i' or ch == 'o' or ch == 'u' or ch == 'A'
       or ch == 'E' or ch == 'I' or ch == 'O' or ch == 'U'):
        return True
    else:
        return False


def calcAverageScore(scores, counts):
    # Takes in array of scores and array of counts
    scaled_scores = []
    sum_counts = sum(counts)
    for i in range(len(scores)):
        scaled_scores.append(scores[i] * counts[i])

    avg = round(sum(scaled_scores)/sum_counts, 2)

    return avg, sum_counts


def pullGameScores(title):
    mc_scores = []
    mc_scores_count = []
    user_scores = []
    user_scores_count = []
    developers = []
    genres = []

    game_urls, platforms = getValidGameURLs(title)

    for i in range(len(game_urls)):
        # print(game_urls[i])
        game_data = pullGameDataFromURL(game_urls[i])
        mc_scores.append(game_data["Metascore"])
        mc_scores_count.append(game_data["Metascore count"])
        user_scores.append(game_data["User score"])
        user_scores_count.append(game_data["User score count"])

        for i in game_data["Developers"]:
            if i not in developers:
                developers.append(i)

        for i in game_data["Genres"]:
            if i not in genres:
                genres.append(i)

    mc_scores_num = [float(i) for i in mc_scores if isNumber(i)]
    user_scores_num = [float(i) for i in user_scores if isNumber(i)]

    mc_count_num = [float(i) for i in mc_scores_count if isNumber(i)]
    user_count_num = [float(i) for i in user_scores_count if isNumber(i)]

    mc_score_avg, mc_sum_counts = calcAverageScore(mc_scores_num, mc_count_num)
    user_score_avg, user_sum_counts = calcAverageScore(
        user_scores_num, user_count_num)

    dev_list = listToString(developers)
    plats_list = listToString(platforms).replace('-', ' ')
    gens_list = listToString(genres)

    # Format for printing!
    if(printout):
        print('\n\'%s\' is %s%s game developed by%s.' %
              (title, 'an' if isVowel(gens_list[1]) else 'a', gens_list, dev_list))

        print('\nIt is available on%s.' % plats_list)

        print('\nGame Scores: ')

        for x in range(len(platforms)):
            print('\n The metacritic score on %s is %s (n = %s), and the user score is %s (n = %s).\n' %
                  (platforms[x], mc_scores[x], mc_scores_count[x], user_scores[x], user_scores_count[x]))
        print('\nAvg Meta Score:', mc_score_avg,
              '(n = %d)' % mc_sum_counts)
        print('\nAvg User Score:', user_score_avg,
              '(n = %d)' % user_sum_counts)


def pullGameDataFromURL(url):
    # Takes a URL, returns a dictionary with game data.

    response = requests.get(url, headers=user_agent)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Metacritic Score
    try:
        mc_score = soup.find('div', class_='metascore_summary').find(
            "span").text  # pulls metascore summary value
        mc_score = mc_score if mc_score.isnumeric() else 'None'
    except:
        mc_score = None

    # Metacritic Score Count
    try:
        mc_score_count = soup.find('div', class_='metascore_summary').find(
            'span', class_='count').find('a').find('span').text.strip().split(" ")[0]
        if mc_score_count == '0':
            mc_score_count = None
    except:
        mc_score_count = None

    # User Score
    try:
        user_score = soup.find('div', class_='userscore_wrap').find(
            'div', class_='metascore_w').text.strip()
        user_score = user_score if isNumber(user_score) else 'None'
    except:
        user_score = None

    # User Score Count
    try:
        user_score_count = soup.find('div', class_='userscore_wrap').find(
            'span', class_="count").find('a').text.strip().split(' ')[0]
        if user_score_count == '0':
            user_score_count = None
    except:
        user_score_count = None

    # Developers
    developers = []
    developer_list = []

    try:
        developer_list = soup.find_all("li", class_='developer')
    except:
        pass

    try:
        for devs in developer_list[0].find_all('span', class_='data'):
            developers.append(devs.text.strip())
    except:
        pass

    # Genre list
    genres = []
    genre_list = []
    try:
        genre_list = soup.find_all("li", class_='product_genre')

        for gens in genre_list[0].find_all('span', class_='data'):
            genres.append(gens.text.strip())
    except:
        pass

    data = {'Metascore': mc_score, 'Metascore count': mc_score_count,
            'User score': user_score, 'User score count': user_score_count, 'Developers': developers, 'Genres': genres}

    return data


def main():
    # On startup, ask for inputs
    global platforms_test

    print("\nWhich game are you looking for?")
    game_title = input()
    # TO DO: Suggest alternatives if misspelled? From MC search...

    if not game_title:
        print('You have failed spectacularly. I will end myself.')
        exit()

    print('\nOn which platform? (space separated entries)')
    print('Options: ', listToString(platforms_test))
    print("\n(Hit enter to search all by default)")
    plat_input = input().split(" ")

    if plat_input[0] == '':
        pass

    else:
        for plat in plat_input:
            if plat not in platforms_test:
                print("that's not an option you absolute buffoon")
                exit()
        platforms_test = plat_input
        print('Excellent Choice, stranger! ')

    print('searching... \n')

    pullGameScores(game_title)


if __name__ == "__main__":
    # Standard sytnax
    main()
