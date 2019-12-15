'''
@author: hinfsynz
@created: 12/08/2019
@note: this file is used to clean the raw poem dictionary file converted from sougou cell file *.scel
'''

import os, fnmatch
from os import path

dict_files = fnmatch.filter(os.listdir('./input/'), '*.txt')
for dict_file in dict_files:
    words_list = []
    #print(path.splitext(dict_file)[0])
    with open('./input/' + dict_file, 'r') as f:
        for line in f:
            if 'x:1' in line: continue    # skip the separators
            words = line.split()[0]
            words_list.append(words)
    with open('./input/' + path.splitext(dict_file)[0] + '_clean.txt', 'w') as f:
        for words in words_list:
            f.write(words)
            f.write('\n')
