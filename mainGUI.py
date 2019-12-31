try:
    from tkinter import ttk   # Python3
    from tkinter import filedialog as td
    from tkinter import simpledialog as sd
    from tkinter import messagebox as tm
    import tkinter as tk
    from queue import Queue
except ImportError:
    import Tkinter as tk    # Python 2
    import ttk
    import tkFileDialog as td
    import Queue
    import tkMessageBox as tm
import datetime
import csv
from calendar import monthrange
from tkcalendar import Calendar, DateEntry
from os import path
import platform
import EZName
import util.scel2txt as scel2txt
import util.fetch_syllables as fetch_syllables
import util.segment_poem as segment_poem
import requests

class Menu:
    canvas = None
    configQueue = None
    def __init__(self, master, configQueue):
        self.master = master
        self.configQueue = configQueue
        self.menu = tk.Menu(master)
        master.config(menu=self.menu)

        # add File menu
        self.fileMenu = tk.Menu(self.menu)
        self.menu.add_cascade(label='File', menu=self.fileMenu)
        self.fileMenu.add_command(label='Import Names from File...',
                                  command=self.importNamesFromFile)
        self.fileMenu.add_command(label='Clear Names from List',
                                  command=self.clearNamesFromList)
        self.fileMenu.add_command(label='Save Names to File ...',
                                  command=self.saveNamesToFavourite)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label='Exit', command=self.exit)
        
        # add Tools menu
        self.toolsMenu = tk.Menu(self.menu)
        self.menu.add_cascade(label='Tools', menu=self.toolsMenu)
        self.toolsMenu.add_command(label='Convert poem collection (*.scel --> *.txt)',
                                   command=self.convertCellDict)
        self.toolsMenu.add_command(label='Fetch (pinyin) syllable pronunciation difficulty',
                                   command=self.fetchSyllableDifficulty)
        self.toolsMenu.add_command(label='Segment poem to words',
                                   command=self.segmentPoemWords)

        # add Run menu
        self.runMenu = tk.Menu(self.menu)
        self.subRunMenu = tk.Menu(self.runMenu)
        self.menu.add_cascade(label='Run', menu=self.runMenu)
        self.runMenu.add_command(label='Run with current configuration',
                                 command=self.runWithCurrentConfig)
        self.runMenu.add_cascade(label='Load A Recent Run...',
                                 menu=self.subRunMenu)
        self.runMenu.add_command(label='Show Sample Run',
                                 command=self.sampleRun)

        # add a FIFO queue to save the recent run configurations
        #self.configQueue = Queue(maxsize=10)
        # add sample runs, which will be flushed later by the user's input
        #self.configQueue.put(['-s', 'Zhang', '-g', 'M', '-m', '05', '-d', '09', '-y', '2020', '-H', '10', '-n', 'True'])
        #self.configQueue.put(['-s', 'Wang', '-g', 'M', '-m', '03', '-d', '30', '-y', '2020', '-n', 'True'])
        #self.configQueue.put(['-s', 'Li', '-g', 'F', '-m', '10', '-d', '12', '-y', '2020', '-H', '6', '-n', 'False'])

        for i in range(len(self.configQueue.queue)):
            args = self.configQueue.queue[i]
            if '-H' in args:
                configStr = '{0}/{1}/{2}:{6}, surname: {3}, gender: {4}, score: {5}' \
                            .format(args[5], args[7], args[9], args[1], args[3], args[13], args[11])
            else:
                configStr ='{0}/{1}/{2}, surname: {3}, gender: {4}, score: {5}' \
                            .format(args[5], args[7], args[9], args[1], args[3], args[11])
            self.subRunMenu.add_command(label='Run {0}: {1}'.format(i+1, configStr), command=lambda idx=i: self.runWithRecentConfig(idx))

        # add a help menu
        self.helpMenu = tk.Menu(self.menu)
        self.menu.add_cascade(label='Help', menu=self.helpMenu)
        self.helpMenu.add_command(label='Copyright', command=self.popupCopyrightText)
        self.helpMenu.add_command(label='Download Latest Version', command=self.downloadZip)

    def popupCopyrightText(self):
        popup_cp_window = tk.Tk()
        popup_cp_window.wm_title('EZName License')
        textbox = tk.Text(popup_cp_window, font=('Calibri', 12, 'bold'))
        textbox.pack()
        license_statements = 'MIT License'
        with open('LICENSE', 'r') as f:
            license_statements = f.read()
        textbox.insert(tk.END, license_statements)
        textbox.config(state=tk.DISABLED)
        okayBtn = tk.Button(popup_cp_window, text='Ok', command=popup_cp_window.destroy)
        okayBtn.pack()
        popup_cp_window.mainloop()

    def downloadZip(self):
        download_url = 'https://github.com/hinfsynz/EZName/archive/master.zip'
        r = requests.get(download_url)
        with open('EZName.zip', 'wb') as f:
            f.write(r.content)
        if r.status_code == 200:
            print('Successfully download the latest version of EZName')
        else:
            print('Something went wrong')

    def exit(self):
        if tm.askokcancel('Quit', 'Do you want to quit?'):
            with open('./input/recentRuns.config', 'w', newline='') as csvFile:
                writer = csv.DictWriter(csvFile, fieldnames=['Name', 'Gender', 'Month', 'Day', 'Year', 'Hour', 'Score'])
                writer.writeheader()
                for row in self.configQueue.queue:
                    if len(row) > 11:
                        writer.writerow({'Name': row[1], 'Gender': row[3], 'Month': row[5],
                                         'Day': row[7], 'Year': row[9], 'Hour': row[11],
                                         'Score': row[13]})
                    else:
                        writer.writerow({'Name': row[1], 'Gender': row[3], 'Month': row[5],
                                         'Day': row[7], 'Year': row[9], 'Hour': 'N/A',
                                         'Score': row[11]})
        self.master.destroy()

    def bindCanvasObj(self, canvas):
        self.canvas = canvas

    def runWithCurrentConfig(self):
        if self.canvas:
            lastName = self.canvas.lastNameEntry.get()
            if not lastName:
                print('last name is missing!')
                return
            month = self.canvas.months.index(self.canvas.comboMonth.get()) + 1
            day = self.canvas.comboDay.get()
            year = self.canvas.comboYear.get()
            gender = self.canvas.comboGender.get()
            if self.canvas.cutoffScoreEntry.get():
                cutoff_score = int(self.canvas.cutoffScoreEntry.get())
            else:
                cutoff_score = -99
            if self.canvas.comboHour['state'].string == 'normal':
                hour = self.canvas.comboHour.get()
                args = ['-s', str(lastName), '-g', str(gender), '-m',
                        str(month), '-d', str(day), '-y', str(year), '-H', str(hour), '-n', str(cutoff_score)]
                print('Running exact mode\nsearching baby name for surname {0}, gender: {1} date of birth: {2}-{3}-{4}, hour: {5}' \
                      .format(args[1], args[3], args[5], args[7], args[9], args[11]))
            else:
                hour = None
                args = ['-s', str(lastName), '-g', str(gender), '-m',
                        str(month), '-d', str(day), '-y', str(year), '-n', str(cutoff_score)]
                print('Running fuzzy mode\nsearching for baby name for surname {0}, gender: {1}, date of birth: {2}-{3}-{4}' \
                      .format(args[1], args[3], args[5], args[7], args[9]))
            num_of_matches = int(float(self.canvas.numOfNamesSlider.get()))
            if self.canvas.cutoffScoreEntry.get():
                cutoff_score = int(self.canvas.cutoffScoreEntry.get())
                name_tuples = EZName.main(args, num_of_matches=num_of_matches, cutoff_score=cutoff_score)   # run the main program
            else:
                name_tuples = EZName.main(args, num_of_matches=num_of_matches)

            if not hour:
                for hour_tuple in name_tuples:
                    for tuple in hour_tuple:
                        self.canvas.nameListBox.insert('', 'end', values=(tuple[0], tuple[1], tuple[2], tuple[3]))
            else:
                for tuple in name_tuples:
                    self.canvas.nameListBox.insert('', 'end', values=(tuple[0], tuple[1], tuple[2], tuple[3]))
            print('Done!')
        else:
            print('Error! Canvas is not initialized!')
            return

    def runWithRecentConfig(self, idx):
        print('config: {}'.format(idx))
        args = self.configQueue.queue[idx]
        name_tuples = EZName.main(args, num_of_matches=int(self.canvas.numOfNamesSlider.get()))
        if '-H' not in args:
            for hour_tuple in name_tuples:
                for tuple in hour_tuple:
                    self.canvas.nameListBox.insert('', 'end', values=(tuple[0], tuple[1], tuple[2], tuple[3]))
        else:
            for tuple in name_tuples:
                self.canvas.nameListBox.insert('', 'end', values=(tuple[0], tuple[1], tuple[2], tuple[3]))
        print("Done running recent config '{}'".format(idx+1))

    def sampleRun(self):
        args = ['-s', '李', '-g', 'M', '-y', '2020', '-m', '7', '-d', '3', '-H', '10']
        print('Running test mode\nsearching baby name for surname {0}, gender: {1}, date of birth: {2}-{3}-{4}' \
              .format(args[1], args[3], args[7], args[9], args[5]))
        name_tuples = EZName.main(args, num_of_matches=5)
        for tuple in name_tuples:
            self.canvas.nameListBox.insert('', 'end', values=(tuple[0], tuple[1], tuple[2], tuple[3]))
        print('Done! Exiting test mode...')


    def convertCellDict(self):
        #args = ['/Users/hinfsynz/Downloads/楚辞全部语句.scel', '/Users/hinfsynz/Downloads/test.txt']
        scelFile = td.askopenfilename(initialdir='/', title='Open a *.scel file to convert',
                                      filetypes=[('Sougou Cell Thesaurus files', '*.scel')])
        txtFile = sd.askstring('Input', 'Give a name to the expected *.txt file', parent=self.master)
        if '.txt' not in txtFile:
            txtFile += '.txt'
        args = [scelFile, './input/{}'.format(txtFile)]
        print('converting {0} to {1}'.format(args[0], args[1]))
        scel2txt.main(args)

    def fetchSyllableDifficulty(self):
        fetch_syllables.main()

    def segmentPoemWords(self):
        segment_poem.main()

    def importNamesFromFile(self):
        nameFile = td.askopenfilename(initialdir='./name/',title='Import A Name File',
                                      filetypes=[('Baby Names File', '*.csv'), ('All Files', '*')])
        if nameFile:
            with open(nameFile, 'r') as f:
                for line in f:
                    if '//' in line: continue   # skip the commented out lines
                    hour = line.split(',')[0].strip()
                    name = line.split(',')[1].strip()
                    pinyin = line.split(',')[2].strip()
                    score = line.split(',')[3].strip()
                    if self.canvas:
                        self.canvas.nameListBox.insert('', 'end', values=(hour, name, pinyin, score))

    def clearNamesFromList(self):
        if self.canvas:
            for i in self.canvas.nameListBox.get_children():
                self.canvas.nameListBox.delete(i)

    def saveNamesToFavourite(self):
        if self.canvas.nameListBox.get_children():
            with open('babynames.csv', 'w', newline='') as csvFile:
                writer = csv.DictWriter(csvFile, fieldnames=['hour', 'name', 'pinyin', 'score'])
                writer.writeheader()
                for i in self.canvas.nameListBox.get_children():
                    row = self.canvas.nameListBox.item(i)['values']
                    writer.writerow({'hour': row[0], 'name':row[1], 'pinyin':row[2], 'score':row[3]})


class Canvas:

    menu = None
    configQueue = None

    def __init__(self, master, configQueue):

        self.master = master
        self.configQueue = configQueue
        self.calIcon = tk.PhotoImage(file='resource/cal_icon_2.png').subsample(10)

        #self.background_image = tk.PhotoImage(file='resource/gui_bg.png')
        #self.background_label = tk.Label(master, image=self.background_image)
        #self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.inputFrame = tk.Frame(master)
        self.inputFrame.grid(row=0, column=0)

        self.labelDate = tk.Label(self.inputFrame, font=('Arial', 14, 'bold'), text='Pick your due date')
        self.labelDate.grid(column=0, row=1, pady=10)

        self.labelMonth = tk.Label(self.inputFrame, text='Month')
        self.labelMonth.grid(column=0, row=2, sticky=tk.W)
        self.labelDay = tk.Label(self.inputFrame, text='Day')
        self.labelDay.grid(column=1, row=2, sticky=tk.W)
        self.labelYear = tk.Label(self.inputFrame, text='Year')
        self.labelYear.grid(column=2, row=2, sticky=tk.W)
        self.labelCalendar = tk.Label(self.inputFrame, text='Calendar')
        self.labelCalendar.grid(column=3, row=2, sticky=tk.W)
        self.labelHour = tk.Label(self.inputFrame, text='Hour (Optional)')
        self.labelHour.grid(column=4, row=2, sticky=tk.W)

        self.today = datetime.date.today()
        # add a combobox for month selection
        self.months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                  "November", "December"]
        self.comboMonth = ttk.Combobox(self.inputFrame, height=10, width=7, values=self.months)
        self.comboMonth.grid(column=0, row=3, sticky=tk.W)
        self.comboMonth.set(self.months[self.today.month - 1])

        # add a combobox for year selection
        years = [i for i in range(self.today.year, self.today.year + 5)]
        self.comboYear = ttk.Combobox(self.inputFrame, height=20, width=5, values=years)
        self.comboYear.grid(column=2, row=3, sticky=tk.W)
        self.comboYear.set(self.today.year)

        # add a combobox for day selection
        monthdays = monthrange(int(self.comboYear.get()), self.months.index(self.comboMonth.get()) + 1)[1]
        self.comboDay = ttk.Combobox(self.inputFrame, height=20, width=5, values=[i for i in range(1, monthdays + 1)])
        self.comboDay.grid(column=1, row=3, sticky=tk.W)
        self.comboDay.set(self.today.day)

        # add a combobox for hour selection
        self.comboHour = ttk.Combobox(self.inputFrame, height=20, width=5, values=[i for i in range(0, 24)], state='disabled')
        self.comboHour.grid(column=4, row=3)
        self.comboHour.current(0)

        # add a radiobutton for lookup mode
        self.lookupMode = tk.IntVar(self.inputFrame, 1)
        lookupModeValues = {"Fuzzy Mode": 1, "Exact Mode": 2}
        btnNum = 0
        for (text, value) in lookupModeValues.items():
            self.btnModeSelect = tk.Radiobutton(self.inputFrame, text=text, variable=self.lookupMode, value=value, command=self.selectMode)
            self.btnModeSelect.grid(column=6, row=3 + btnNum)
            btnNum += 1

        self.comboMonth.bind("<<ComboboxSelected>>", self.monthSelectionCallback)
        self.comboDay.bind("<<ComboboxSelected>>", self.daySelectionCallback)
        self.comboYear.bind("<<ComboboxSelected>>", self.yearSelectionCallback)
        self.comboHour.bind("<<ComboboxSelected>>", self.hourSelectionCallback)
        self.calBtn = ttk.Button(self.inputFrame, image=self.calIcon, command=self.popupCal, width=1)
        self.calBtn.grid(column=3, row=3)

        # add a label and textbox for last name entry
        self.lastNameLabel = tk.Label(self.inputFrame, font=('Arial', 14, 'bold'), text='Your last name')
        self.lastNameLabel.grid(column=0, row=5, pady=10)
        self.lastNameEntry = tk.Entry(self.inputFrame, width=10)
        self.lastNameEntry.grid(column=1, row=5)

        # add a label and combobox for baby gender
        self.genderLabel = tk.Label(self.inputFrame, font=('Arial', 14, 'bold'), text='Gender')
        self.genderLabel.grid(column=2, row=5)
        self.comboGender = ttk.Combobox(self.inputFrame, height=2, width=2, values=['M', 'F'])
        self.comboGender.grid(column=3, row=5)
        self.comboGender.set('M')


        # add a checkbox to indicate if enable name scoring
        self.enableNameScoring = tk.BooleanVar(self.inputFrame, True)
        self.chkBtn = ttk.Checkbutton(self.inputFrame, variable=self.enableNameScoring, onvalue=True, offvalue=False,
                                      text='Get name score?', command=self.checkNameScore)
        self.chkBtn.grid(column=0, row=6)


        self.style = ttk.Style()
        self.style.configure('my.TButton', font=('Arial', 16, 'bold'), foreground='green', background='black')

        # add a text entry for cutoff score if name scoring is enabled
        self.cutoffScoreLabel = tk.Label(self.inputFrame, text='Cutoff Score (0 ~ 100)')
        self.cutoffScoreLabel.grid(column=1, row=6)
        self.cutoffScoreEntry = tk.Entry(self.inputFrame, width=3)
        self.cutoffScoreEntry.grid(column=2, row=6)

        # add the run button
        self.runBtn = ttk.Button(self.inputFrame, text='Find Names', style='my.TButton', width=10,
                                 command=self.findNames)
        self.runBtn.grid(column=3, row=6, pady=10)

        # add a slider to get the number of names for one time output
        self.sliderLabel = ttk.Label(self.inputFrame)
        self.sliderLabel.grid(column=5, row=6, sticky=tk.W)
        self.sliderLabel.configure(foreground='Green', font=('Calibri', 13, 'bold'), text='5')
        self.numOfNamesSlider = ttk.Scale(self.inputFrame, from_=1, to=10, orient=tk.HORIZONTAL,
                                         command=self.updateNumOfNamesWanted)
        self.numOfNamesSlider.grid(column=4, row=6, padx=10)
        self.numOfNamesSlider.set(5)
        self.numOfNamesSlider.bind('<Enter>', self.on_enter_slider)
        self.numOfNamesSlider.bind('<Leave>', self.on_leave_slider)
        self.sliderHoverText = ttk.Label(self.inputFrame, text='Hover over the slider\nfor hint')
        self.sliderHoverText.configure(foreground='Orange', font=('Calibri', 11))
        self.sliderHoverText.grid(column=4, row=5)

        # add a tableview to show the found names
        self.tableFrame = tk.Frame(master)
        self.tableFrame.grid(row=1, columnspan=4)

        # customize the treeview style
        self.style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Calibri', 17))  # Modify the font of the body
        self.style.configure("mystyle.Treeview.Heading", font=('Calibri', 15, 'bold'))  # Modify the font of the headings
        self.style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])  # Remove the borders
        self.labelTable = tk.Label(self.tableFrame, text="Found Names", font=("Arial", 20, 'bold'))
        self.labelTable.grid(row=0, columnspan=4)
        # create Treeview with 3 columns
        self.tableCols = ('Hour', 'Name', 'Pinyin', 'Score')
        self.nameListBox = ttk.Treeview(self.tableFrame, style='mystyle.Treeview', columns=self.tableCols, show='headings')
        # set column headings
        for col in self.tableCols:
            self.nameListBox.heading(col, text=col)
        if platform.system() == 'Darwin':
            self.nameListBox.bind('<Button-2>', self.popupMenu)
        else:  # Windows
            self.nameListBox.bind('<Button-3>', self.popupMenu)
        self.nameListBox.bind('<<TreeviewSelect>>')
        self.nameListBox.grid(row=1, rowspan=10, column=0, columnspan=4, padx=20, sticky=tk.W)

        # add a scrollbar and attach it to the treeview
        self.nameListScroll = ttk.Scrollbar(self.tableFrame, orient='vertical', command=self.nameListBox.yview)
        #self.nameListScroll.place(height=400)
        self.nameListBox.configure(yscrollcommand=self.nameListScroll.set)
        self.nameListScroll.grid(row=1, column=4, sticky=tk.E)

        # create a popup menu for the right click activity
        self.treeRightClickMenu = tk.Menu(self.tableFrame, tearoff=0)
        self.treeRightClickMenu.add_command(label='Save Selected Items', command=self.saveSelectedItems)
        self.treeRightClickMenu.add_command(label='Save All Items', command=self.saveAllItems)
        self.treeRightClickMenu.add_command(label='Clear Selected Items', command=self.clearSelectedItems)
        self.treeRightClickMenu.add_command(label='Clear All Items', command=self.clearAllItems)

    def bindMenuObj(self, menu):
        self.menu = menu

    def updateNumOfNamesWanted(self, event):
        idx = int(float(event))
        self.sliderLabel.configure(foreground='Green', font=('Calibri', 13, 'bold'), text=str(idx))

    def on_enter_slider(self, event):
        self.sliderHoverText.configure(foreground='Blue', font=('Calibri', 11),
                                       text='Number of names you\nwant to find out')

    def on_leave_slider(self, event):
        self.sliderHoverText.configure(foreground='Orange', font=('Calibri', 11),
                                       text='Hover over the slider\nfor hint')

    def popupMenu(self, event):
        try:
            self.treeRightClickMenu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            # make sure to release the grab
            self.treeRightClickMenu.grab_release()

    def saveSelectedItems(self):
        saveAsFile = td.asksaveasfilename(filetypes=[('Baby Names File', '*.csv')],
                                      defaultextension=[('Baby Names File', '*.csv')])
        if saveAsFile and self.nameListBox.selection():
            print('Saving selected items to file {}'.format(saveAsFile))
            with open(saveAsFile, 'w', newline='') as f:
                csvWriter = csv.DictWriter(f, fieldnames=['hour', 'name', 'pinyin', 'score'])
                csvWriter.writeheader()
                for i in self.nameListBox.selection():
                    row = self.nameListBox.item(i)['values']
                    csvWriter.writerow({'hour': row[0], 'name':row[1], 'pinyin': row[2], 'score': row[3]})
            print('Done saving!')
        elif not self.nameListBox.selection():
            print('No item was selected!')

    def saveAllItems(self):
        saveAsFile = td.asksaveasfilename(filetypes=[('Baby Names File', '*.csv')],
                                          defaultextension=[('Baby Names File', '*.csv')])
        if saveAsFile and self.nameListBox.get_children():
            print('Saving selected items to file {}'.format(saveAsFile))
            with open(saveAsFile, 'w', newline='') as f:
                csvWriter = csv.DictWriter(f, fieldnames=['hour', 'name', 'pinyin', 'score'])
                csvWriter.writeheader()
                for i in self.nameListBox.get_children():
                    row = self.nameListBox.item(i)['values']
                    csvWriter.writerow({'hour': row[0], 'name': row[1], 'pinyin': row[2], 'score': row[3]})
            print('Done saving!')
        elif not self.nameListBox.get_children():
            print('No name has been loaded!')

    def clearSelectedItems(self):
        for i in self.nameListBox.selection():
            self.nameListBox.delete(i)

    def clearAllItems(self):
        for i in self.nameListBox.get_children():
            self.nameListBox.delete(i)

    def findNames(self):
        lastName = self.lastNameEntry.get()
        if not lastName:
            print('last name is missing!')
            return
        month = self.months.index(self.comboMonth.get()) + 1
        day = self.comboDay.get()
        year = self.comboYear.get()
        gender = self.comboGender.get()
        if self.cutoffScoreEntry.get():
            cutoff_score = int(self.cutoffScoreEntry.get())
        else:
            cutoff_score = -99
        if self.comboHour['state'].string == 'normal':
            hour = self.comboHour.get()
            args = ['-s', str(lastName), '-g', str(gender), '-m',
                    str(month), '-d', str(day), '-y', str(year), '-H', str(hour), '-n', str(cutoff_score)]
            print('Running exact mode\nsearching baby name for surname {0}, gender: {1} date of birth: {2}-{3}-{4}, hour: {5}' \
                .format(args[1], args[3], args[5], args[7], args[9], args[11]))
        else:
            hour = None
            args = ['-s', str(lastName), '-g', str(gender), '-m',
                    str(month), '-d', str(day), '-y', str(year), '-n', str(cutoff_score)]
            print('Running fuzzy mode\nsearching for baby name for surname {0}, gender: {1}, date of birth: {2}-{3}-{4}' \
                  .format(args[1], args[3], args[5], args[7], args[9]))
        num_of_matches = int(float(self.numOfNamesSlider.get()))
        name_tuples = EZName.main(args, num_of_matches=num_of_matches, cutoff_score=cutoff_score)  # run the main program
        if not hour:
            for hour_tuple in name_tuples:   # each hour has 'num_of_matches' names found
                for tuple in hour_tuple:
                    self.nameListBox.insert('', 'end', values=(tuple[0], tuple[1], tuple[2], tuple[3]))
        else:
            for tuple in name_tuples:
                self.nameListBox.insert('', 'end', values=(tuple[0], tuple[1], tuple[2], tuple[3]))
        print('Done!')

        # update the label of the 'Load Recent Run' submenu
        if '-H' in args:  # if 'hour' has been specified
            configStr = '{0}/{1}/{2}:{6}, surname: {3}, gender: {4}, score: {5}' \
                .format(str(month), str(day), str(year), str(lastName), str(gender), str(cutoff_score), str(hour))
        else:
            configStr = '{0}/{1}/{2}, surname: {3}, gender: {4}, score: {5}' \
                .format(str(month), str(day), str(year), str(lastName), str(gender), str(cutoff_score))

        if not self.configQueue.full():  # check the config queue is full or not
            self.configQueue.put(args)
            num_of_recent_runs = len(self.configQueue.queue)
            self.menu.subRunMenu.add_command(label='Run {0}: {1}'.format(num_of_recent_runs, configStr),
                                             command=lambda idx=num_of_recent_runs-1: self.menu.runWithRecentConfig(idx))
        else:
            unwanted_config = self.configQueue.get()
            self.configQueue.put(args)
            for i in range(len(self.configQueue.queue)):
                recent_args = self.configQueue.queue[i]
                if '-H' in recent_args:  # if 'hour' has been specified
                    recent_configStr = '{0}/{1}/{2}:{6}, surname: {3}, gender: {4}, score: {5}' \
                        .format(str(recent_args[5]), str(recent_args[7]), str(recent_args[9]), str(recent_args[1]),
                                str(recent_args[3]), str(recent_args[13]), str(recent_args[11]))
                else:
                    recent_configStr = '{0}/{1}/{2}, surname: {3}, gender: {4}, score: {5}' \
                        .format(str(recent_args[5]), str(recent_args[7]), str(recent_args[9]), str(recent_args[1]),
                                str(recent_args[3]), str(recent_args[11]))
                self.menu.subRunMenu.entryconfigure(i, label='Run {0}: {1}'.format(i+1, recent_configStr),
                                                    command=lambda idx=i: self.menu.runWithRecentConfig(idx))
            #self.configQueue.put(args)
            #num_of_recent_runs = len(self.configQueue.queue)
            #self.menu.subRunMenu.add_c(label='Run {0}: {1}'.format(num_of_recent_runs-1, configStr),
                                            # command=lambda idx=num_of_recent_runs - 1: self.menu.runWithRecentConfig(idx))

    def checkNameScore(self):
        print(self.enableNameScoring.get())
        if self.enableNameScoring.get():
            self.cutoffScoreEntry.configure(state='normal')
        else:
            self.cutoffScoreEntry.configure(state='disabled')


    def monthSelectionCallback(self, event):
         print('selected month: {}'.format(self.comboMonth.get()))
         # update the no. of days every time when the month is changed
         print('update the no. of days')
         self.updateMonthDays()


    def daySelectionCallback(self, event):
        print('selected month: {}'.format(self.comboDay.get()))

    def yearSelectionCallback(self, event):
        print('selected year: {}'.format(self.comboYear.get()))
        # update the no. of days when the year is changed considering the leap year
        print('update the no. of days')
        self.updateMonthDays()

    def hourSelectionCallback(self, event):
        print('selected hour (optional): {}'.format(self.comboHour.get()))

    def updateMonthDays(self):
        monthdays = monthrange(int(self.comboYear.get()), self.months.index(self.comboMonth.get()) + 1)[1]
        self.comboDay['values'] = [i for i in range(1, monthdays + 1)]

    def selectMode(self):
        mode = self.lookupMode.get()
        if mode == 1:
            self.comboHour.configure(state='disabled')
        else:
            self.comboHour.configure(state='normal')

    def popupCal(self):
        def updateDate():
            sel_date = self.cal.selection_get()
            self.comboYear.set(sel_date.year)
            self.comboMonth.set(self.months[sel_date.month-1])
            self.comboDay.set(sel_date.day)
            self.top.destroy()
        mindate = self.today
        maxdate = self.today + datetime.timedelta(weeks=300)
        self.top = tk.Toplevel(self.master)
        self.cal = Calendar(self.top, font="Arial 14", selectmode='day', locale='en_US',
                       mindate=mindate, maxdate=maxdate, disabledforeground='red',
                       cursor="hand1", year=self.today.year, month=self.today.month, day=self.today.day)
        self.cal.pack(fill="both", expand=True)
        ttk.Button(self.top, text='OK', command=updateDate).pack()

def on_closing():
    if tm.askokcancel('Quit', 'Do you want to quit?'):
        with open('./input/recentRuns.config', 'w', newline='') as csvFile:
            writer = csv.DictWriter(csvFile, fieldnames=['Name', 'Gender', 'Month', 'Day', 'Year', 'Hour', 'Score'])
            writer.writeheader()
            for row in configQueue.queue:
                if len(row) > 12:
                    writer.writerow({'Name': row[1], 'Gender': row[3], 'Month': row[5],
                                     'Day': row[7], 'Year': row[9], 'Hour': row[11],
                                     'Score': row[13]})
                else:
                    writer.writerow({'Name': row[1], 'Gender': row[3], 'Month': row[5],
                                     'Day': row[7], 'Year': row[9], 'Hour': 'N/A',
                                     'Score': row[11]})
        app.destroy()

def loadRunConfig(configQueue):
    if path.exists('./input/recentRuns.config'):
        with open('./input/recentRuns.config', newline='') as f:
            csvReader = csv.DictReader(f)
            for row in csvReader:
                if row['Hour'] != 'N/A':
                    args = ['-s', row['Name'], '-g', row['Gender'], '-m', row['Month'],
                            '-d', row['Day'], '-y', row['Year'], '-H', row['Hour'],
                            '-n', row['Score']]
                else:
                    args = ['-s', row['Name'], '-g', row['Gender'], '-m', row['Month'],
                            '-d', row['Day'], '-y', row['Year'], '-n', row['Score']]
                configQueue.put(args)

if __name__ == "__main__":
    app = tk.Tk()
    app.geometry('850x500')
    app.title('EZName v1.0 (Alpha Release)')
    app.resizable(False, False)   # make the window non-resizeable
    configQueue = Queue(maxsize=10)
    loadRunConfig(configQueue=configQueue)
    menu = Menu(app, configQueue)
    canvas = Canvas(app, configQueue)
    menu.bindCanvasObj(canvas) # bind the canvas object being created to menu in order to update the user selection
    canvas.bindMenuObj(menu)  # bind the menu object being created to canvas to update the menu dynamically
    app.protocol('WM_DELETE_WINDOW', on_closing)
    app.mainloop()