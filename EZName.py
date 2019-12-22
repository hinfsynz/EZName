try:
    from bs4 import BeautifulSoup
except ImportError:
    print("[!_!]ERROR INFO: You have to install bs4 module.")
    exit()

try:
    import requests
except ImportError:
    print("[!_!]ERROR INFO: You have to install requests module.")
    exit()

try:
    import ngender
except ImportError:
    print("[!_!]ERROR INFO: You have to install ngender module.")
    exit()

try:
    from pypinyin import lazy_pinyin
except ImportError:
    print("[!_!]ERROR INFO: You have to install pypinyin module.")
    exit()

import argparse
import sys
import signal
import csv
from random import randint
from util.boxcalendar import *

SCORE_LINE = 70


def compute_wuxing(year, month, day, hour):
    horoscope = lunarday(year, month, day)
    day_stem = horoscope[2].split('-')[2][0]

    time_stem_branch_list = [
        [u"甲子",u"丙子", u"戊子", u"庚子", u"壬子"],
        [u"乙丑",u"丁丑", u"己丑", u"辛丑", u"癸丑"],
        [u"丙寅",u"戊寅", u"庚寅", u"壬寅", u"甲寅"],
        [u"丁卯",u"己卯", u"辛卯", u"癸卯", u"乙卯"],
        [u"戊辰",u"庚辰", u"壬辰", u"甲辰", u"丙辰"],
        [u"己巳",u"辛巳", u"癸巳", u"己巳", u"丁巳"],
        [u"庚午", u"壬午",u"甲午", u"丙午", u"戊午"],
        [u"辛未",u"癸未", u"乙未", u"丁未", u"己未"],
        [u"壬申",u"甲申", u"丙申", u"戊申", u"庚申"],
        [u"癸酉",u"乙酉", u"丁酉", u"己酉", u"辛酉"],
        [u"甲戌",u"丙戌", u"戊戌", u"庚戌", u"壬戌"],
        [u"乙亥",u"丁亥", u"己亥", u"辛亥", u"癸亥"]
    ]
    sky_branch = [u'甲', u'乙', u'丙', u'丁', u'戊', u'己', u'庚', u'辛', u'壬', u'癸']

    index = 0
    for index in range(10):
        if day_stem == sky_branch[index]:
            break

    index_X = index - 5 if index >= 5 else index
    index_Y = int(hour / 2)

    # Generate horoscope
    horoscope = horoscope[2] + '-' + time_stem_branch_list[index_Y][index_X]

    wuxing_dic = {
        u"金": [u"申", u"酉", u"庚", u"辛"],
        u"木": [u"寅", u"卯", u"甲", u"乙"],
        u"水": [u"子", u"亥", u"壬", u"癸"],
        u"火": [u"巳", u"午", u"丙", u"丁"],
        u"土": [u"辰", u"戌", u"丑", u"未", u"戊", u"己"]
    }
    wuxing = {}
    horoscope_list = list(''.join(horoscope.split('-')))
    for key, value in wuxing_dic.items():
        count = 0
        for item in horoscope_list:
            if item in value:
                count += 1
        wuxing[key] = count
    return wuxing


def name_score(name, sur_type=1):
    """
    Get score of name from 1518.com
    :param name: full name
    :param sur_type: surname single(1) or double(2)
    :return: name score
    """
    print('Getting score for name: {0} from http://1518.com...'.format(name))
    header = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
              'Accept-Encoding': 'gzip, deflate',
              'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
              'User-Agent': 'Chrome/63.0.3239.84 Safari/537.36'
              }
    name = str(name.encode('gbk')).split("'")[1].replace('\\x', '%')
    name_url = 'http://m.1518.com/xingming_view.php?word={}&submit1=&FrontType={}'
    page_html = requests.get(name_url.format(name, sur_type), headers=header)
    page_html = page_html.content
    parse_file = BeautifulSoup(page_html, 'lxml')
    name_score = parse_file.select('dt > u strong')
    try:
        score = name_score[0].text.split('分')[0]
    except IndexError:
        score = 0
    finally:
        score = int(score)
    return score


def output_wuxing(year, month, day, hour):
    """
    Compute WuXing with birth datetime.
    :param year:
    :param month:
    :param day:
    :param hour:
    :return: attribute list
    """
    wuxing = compute_wuxing(year, month, day, hour)
    print("[*] 出生日期：%s年%s月%s日, %s时" % (year, month, day, hour))
    attr_list = [attr for attr in wuxing if wuxing[attr] < 2]
    name_attr = list(set(['金', '木', '水', '火', '土']) - set(attr_list))
    print("[*] 五行属性：%s\n" % ', '.join(name_attr))
    return attr_list

def select_name(surname, gender, hour, attr):
    '''
    Select name based on Wuxing attributes and difficulty of the words' pinyin syllables
    gender = M: select words from <chuci>
    gender = F: select words from <shijing>
    '''
    sur_type = 1 if len(surname) == 1 else 2
    match_count = 0
    full_names = []
    name_syllables = []
    name_scores = []
    found_names = get_name_from_wuxing(gender, attr)
    difficulty_dict = load_difficulty_dict()
    while match_count < 5:
        name = found_names[randint(0, len(found_names) - 1)] # randomly pick a name from the matched names
        full_name = surname + name
        # Match gender and general name word.
        if gender != ngender.guess(full_name)[0][0].upper():
            continue
        name_vec = lazy_pinyin(name)
        letters = 0
        isHard = False
        for n in name_vec:
            letters += len(n)
            n = capitalize_first_letter(n)
            if n in difficulty_dict:
                if difficulty_dict[n] != 'Low':
                    isHard = True
        if letters > 6 or isHard:  # if any of the syllables is hard for English speakers, just skip it
            continue

        score = name_score(full_name, sur_type)
        print('score is {0:2d}\n'.format(score))

        full_names.append(full_name)
        name_syllables.append('-'.join(lazy_pinyin(name)))
        name_scores.append(score)

        match_count += 1

    # score the name_scores in a descending order
    # print out the names whose score higher than the threshold in a descending order of their scores
    indices = [index for index, value in sorted(enumerate(name_scores), reverse=True, key=lambda x: x[1])]
    with open('./name/babyname_{0}_{1}.csv'.format(surname, hour), 'w') as f:
        for index in indices:
            f.write(full_names[index] + ', ' + name_syllables[index] + ', ' + str(name_scores[index]))
            f.write('\n')

def get_name_from_wuxing(gender, wuxing_list):
    '''
    get name from word cells based on the wuxing attributes in the given list
    '''
    selected_names = []
    word_cells_list = []
    wuxing_dict = load_wuxing_dict()
    online_wuxing_dict = {}
    if gender.upper() == 'M':
        word_cells_list = [line.strip() for line in open('./input/chuci_clean_cells.txt', 'r')]
    elif gender.upper() == 'F':
        word_cells_list = [line.strip() for line in open('./input/shijing_clean_cells.txt', 'r')]
    else:
        print('Sorry. LGBTQ is not supported. ;-(')
    for word_cells in word_cells_list:
        if len(word_cells) != 2:    # only look at 2-word cells
            continue
        is_match = True
        for word in word_cells:
            if word not in wuxing_dict:
                # word not found in wuxing dictionary, get it from some online website instead
                wuxing = get_wuxing_online(word)
                online_wuxing_dict[word] = wuxing   # save the new word dictionary for file writing
                wuxing_dict[word] = wuxing
            else:
                wuxing = wuxing_dict[word]
            if wuxing not in wuxing_list:
                is_match = False    # as long as there is one word in a cell doesn't match the wuxing attribute, skip it
        if is_match:
            selected_names.append(word_cells)

    # add the new word wuxing to the dictionary file for next run
    if online_wuxing_dict:
        add_new_word_wuxing_to_dict_file(newdict=online_wuxing_dict)

    return selected_names

def add_new_word_wuxing_to_dict_file(newdict):
    with open('./input/wuxing_dict.csv', 'a') as f:
        print('adding new words and their wuxing...\n')
        for word in newdict:
            line = '{0},{1}\n'.format(word, newdict[word])
            print(line)
            f.write(line)
        print('done\n')

def get_wuxing_online(word):
    """
        Get Wuxing attribute from 5156edu.com
        :param word: the word to be looked up
        :return: Wuxing attribute, i.e., '金 木 水 火 土'
    """
    print('Getting wuxing for word: {0} from http://5156edu.com...\n'.format(word))
    header = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
              'Accept-Encoding': 'gzip, deflate',
              'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
              'User-Agent': 'Chrome/63.0.3239.84 Safari/537.36'
              }
    word = str(word.encode('gbk')).split("'")[1].replace('\\x', '%')
    query_url = 'http://xh.5156edu.com/sowx.php?f_key={}&B1='
    page_html = requests.get(query_url.format(word), headers=header)
    page_html = page_html.content
    parse_file = BeautifulSoup(page_html, 'lxml')
    word_wuxing = parse_file.select('p')[2]
    try:
        wuxing = word_wuxing.text.split('：')[1]
    except IndexError:
        wuxing = ''
    return wuxing

def load_difficulty_dict():
    syllable_difficult = {}
    with open('input/pinyin_syllable_difficulty.csv', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            #print(row['Syllable'], row['Difficulty for English speakers'])
            syllable_difficult[row['Syllable']] = row['Difficulty for English speakers']
    return syllable_difficult

def capitalize_first_letter(str):
    capitalizedStr = ''
    for i, letter in enumerate(str):
        if i == 0:
            capitalizedStr = letter.upper()
        else:
            capitalizedStr += letter
    return capitalizedStr

def sigint_handler(signum, frame):
    print('You pressed the Ctrl+C.')
    sys.exit(0)

def load_wuxing_dict():
    wuxing_dict = {}
    with open('input/wuxing_dict.csv', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            wuxing_dict[row['Word']] = row['Wuxing']
    return wuxing_dict

def main(args):
    signal.signal(signal.SIGINT, sigint_handler)

    parser = argparse.ArgumentParser(description="Name children with birth datetime and WuXing balance.")
    parser.add_argument("-s", metavar="surname", required=True, help="Surname.")
    parser.add_argument("-g", metavar="gender", choices=('F', 'M'), required=True, help="Gender(F/M).")
    parser.add_argument("-y", type=int, choices=range(1901, 2049), metavar="year", required=True,
                        help="Year of birth date.")
    parser.add_argument("-m", type=int, choices=range(1, 13), metavar="month", required=True,
                        help="Month of birth date.")
    parser.add_argument("-d", type=int, choices=range(1, 32), metavar="day", required=True,
                        help="Day of birth date.")
    parser.add_argument("-H", type=int, choices=range(0, 24), metavar="hour", required=False,
                        help="Hour of birth datetime.")
    args_tuple = parser.parse_known_args(args=args)

    if args_tuple[0].H:
        attr_list = output_wuxing(args_tuple[0].y, args_tuple[0].m, args_tuple[0].d, args_tuple[0].H)
        select_name(args_tuple[0].s, args_tuple[0].g, args_tuple[0].H, attr_list)
    else:  # no hour is specified, select names for all hours of that day
        for hour in range(0, 24):
            attr_list = output_wuxing(args_tuple[0].y, args_tuple[0].m, args_tuple[0].d, hour)
            select_name(args_tuple[0].s, args_tuple[0].g, hour, attr_list)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_handler)

    parser = argparse.ArgumentParser(description="Name children with birth datetime and WuXing balance.")
    parser.add_argument("-s", metavar="surname", required=True, help="Surname.")
    parser.add_argument("-g", metavar="gender", choices=('F', 'M'), required=True, help="Gender(F/M).")
    parser.add_argument("-y", type=int, choices=range(1901, 2049), metavar="year", required=True,
                        help="Year of birth date.")
    parser.add_argument("-m", type=int, choices=range(1, 13), metavar="month", required=True,
                        help="Month of birth date.")
    parser.add_argument("-d", type=int, choices=range(1, 32), metavar="day", required=True,
                        help="Day of birth date.")
    parser.add_argument("-H", type=int, choices=range(0, 24), metavar="hour", required=False,
                        help="Hour of birth datetime.")
    args = parser.parse_args()

    if args.H:
        attr_list = output_wuxing(args.y, args.m, args.d, args.H)
        select_name(args.s, args.g, args.H, attr_list)
    else:    # no hour is specified, select names for all hours of that day
        for hour in range(0, 24):
            attr_list = output_wuxing(args.y, args.m, args.d, hour)
            select_name(args.s, args.g, hour, attr_list)
