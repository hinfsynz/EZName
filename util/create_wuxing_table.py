'''
@author: hinfsynz
@created: 12/08/2019
@note: this file is used to clean the raw poem dictionary file converted from sougou cell file *.scel
'''

import csv

wuxing_dict = {}
with open('./db/data/rn_wuxing.sql', 'r') as f:
    for line in f:
        if 'INSERT' in line:  # this is an insertion operation
            start_pos = line.find('(')
            end_pos = line.find(')')
            tuples_str = line[start_pos+1: end_pos]
            word = tuples_str.split(',')[-1].split('\'')[1]
            wuxing = tuples_str.split(',')[1].split('\'')[1]
            wuxing_dict[word] = wuxing

with open('./input/wuxing_dict.csv', 'w', newline='') as f:
    col1 = 'Word'
    col2 = 'Wuxing'
    fieldnames = [col1, col2]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for word in wuxing_dict:
        writer.writerow({col1:word, col2:wuxing_dict[word]})
