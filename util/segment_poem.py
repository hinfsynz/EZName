'''
@author: hinfsynz
@created: 12/08/2019
@note: this file is used to segment the poems from <<shijing>> and <<chuci>> to words
'''

import jieba

import os, fnmatch
from os import path

def main():
    dict_files = fnmatch.filter(os.listdir('./input/'), '*_clean.txt')
    for dict_file in dict_files:
        print('Segmenting poem file {} to word cells'.format(dict_file))
        cell_words = []
        with open('./input/' + dict_file, 'r') as f:
            for line in f:
                seg_list = jieba.cut(line.strip(), cut_all=False)
                for seg in seg_list:
                    if seg not in cell_words:   # if the cell word exists, skip it
                        cell_words.append(seg)
        with open('./input/' + path.splitext(dict_file)[0] + '_cells.txt', 'w') as f:
            for cell in cell_words:
                f.write(cell)
                f.write('\n')
    print('Segmenting done!')

if __name__ == '__main__':
    main()
