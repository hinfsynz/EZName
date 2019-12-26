# EZName
Create an easy-to-pronounce and meaningful name from chinese ancient poems for newborns

## Introduction
This project is inspired by another name-creating project "ReName" (https://github.com/repoog/ReName)

The main features of this program include

* Generate a name according to the expected date of birth or a specific hour of the mom's due date. If only the date is provided, the program will generate up to N names for each hour of that day. N is a user-defined parameter.
* The names are picked up from different collections of poems based on the baby's gender. For instance, if it's a boy, the default dictionary is "chuci" (楚辞); if it's a girl, the default source is "shijing" (诗经)
* The candidate names are all easy to pronounce for English speakers because these names' pinyin syllables have low level of difficulty for pronunciation.
* The name dictionary is extendable. Users can download Sogou cell thesaurus (*.scel) and load them in the program to use as the source of names 
* Optionally, the users can decide if the names need to be scored by its "天格/地格/人格/才格". And if they choose to do so, the candidate names will be given in an descending order of this score.

## Installation Instructions
Python3.5 or higher version is required. The binary wheels list below are required to run this program. 
* beautifulsoup4
* jieba
* lxml
* ngender
* pypinyin
* requests
* selenium
* tkcalendar
* urllib3

Run the command below to install the required binary wheels
> python3 -m pip install -r requirements.txt


## Unique Feature
1. All candidate names are examined by their pinyin syllables. The difficulty of syllables are categorized into four levels according to https://resources.allsetlearning.com/
* Low
* Medium
* High
* Very High

Only those names with easy-to-pronounce pinyin syllables for English speakers are selected.

2. The name dictionary is extendable. Users can download more Sogou cell thesaurus in *.scel format and convert them to *.txt format for the use of this program. The conversion utility has been integrated with the GUI


## Usage
* Run from command line
> python3 EZName.py -s 张 -g M -y 2020 -m 5 -d 9

* Run GUI
> python3 mainGUI.py

![image](https://github.com/hinfsynz/EZName/blob/master/resource/EZNameGUIPreview.png)





 
