'''
@author: hinfsynz
@created: 12/07/2019
@note: this file is used to fetch the difficulty level of about 400 pinyin syllables
'''
from selenium import webdriver
import time
import csv

def find_syllable_difficulty(driver, pronunc_links):
    syllable_difficulties = {}
    for link in pronunc_links:
        driver.get(link)
        syllable = link.split('/')[-1]  # the last element of splited data list is the syllable
        elem = driver.find_element_by_class_name("ibox-difficulty")
        difficulty_lvl = elem.text.splitlines()[1]
        print(syllable, difficulty_lvl)
        syllable_difficulties[syllable] = difficulty_lvl
        #time.sleep(2)
    return syllable_difficulties

def main():
    driver = webdriver.Chrome(executable_path=r"/Applications/chromedriver")
    httpaddr = 'https://resources.allsetlearning.com/chinese/pronunciation/syllable'
    driver.get(httpaddr)
    elems = driver.find_elements_by_xpath('//a[@href]')
    pronunc_links = []
    for elem in elems:
         hyperlink = elem.get_attribute('href')
         if '/pronunciation' in hyperlink:
             pronunc_links.append(hyperlink)
    start_pos, end_pos = 0, 0
    for i, link in enumerate(pronunc_links):
        if link.endswith('/pronunciation/A'):
            start_pos = i
        elif link.endswith('/pronunciation/Zuo'):
            end_pos = i
    fine_pronunc_links = pronunc_links[start_pos:end_pos+1]
    #for link in fine_pronunc_links:
    #    print(link)
    time.sleep(2)
    syllable_difficulties = find_syllable_difficulty(driver=driver, pronunc_links=fine_pronunc_links)
    with open('pinyin_syllable_difficulty.csv', 'w', newline='') as f:
        col1 = 'Syllable'
        col2 = 'Difficulty for English speakers'
        fieldnames = [col1, col2]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for syllable in syllable_difficulties:
            writer.writerow({col1:syllable, col2:syllable_difficulties[syllable]})
    driver.close()

if __name__ == "__main__":
    main()