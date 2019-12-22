try:
    from tkinter import ttk   # Python3
    from tkinter import filedialog as td
    from tkinter import simpledialog as sd
    import tkinter as tk
except ImportError:
    import Tkinter as tk    # Python 2
    import ttk
    import tkFileDialog as td
import datetime
from calendar import monthrange
from tkcalendar import Calendar, DateEntry
import EZName
import util.scel2txt as scel2txt
import util.fetch_syllables as fetch_syllables
import util.segment_poem as segment_poem

class Menu:
    canvas = None
    def __init__(self, master):
        self.master = master
        self.menu = tk.Menu(master)
        master.config(menu=self.menu)

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
        self.menu.add_cascade(label='Run', menu=self.runMenu)
        self.runMenu.add_command(label='Run with current configuration',
                                 command=self.runWithConfig)
        self.runMenu.add_command(label='Run...',
                                 command=self.runWithoutConfig)
        self.runMenu.add_command(label='Test Run',
                                 command=self.testRun)

    def bindCanvasObj(self, canvas):
        self.canvas = canvas

    def runWithConfig(self):
        if self.canvas:
            lastName = self.canvas.lastNameEntry.get()
            if not lastName:
                print('last name is missing!')
                return
            month = self.canvas.months.index(self.canvas.comboMonth.get()) + 1
            day = self.canvas.comboDay.get()
            year = self.canvas.comboYear.get()
            gender = self.canvas.comboGender.get()
            if self.canvas.comboHour['state'].string == 'normal':
                hour = self.canvas.comboHour.get()
                args = ['-s', str(lastName), '-g', str(gender), '-m',
                        str(month), '-d', str(day), '-y', str(year), '-H', str(hour)]
                print('Running exact mode\nsearching baby name for surname {0}, gender: {1} date of birth: {2}-{3}-{4}, hour: {5}' \
                      .format(args[1], args[3], args[5], args[7], args[9], args[11]))
            else:
                hour = None
                args = ['-s', str(lastName), '-g', str(gender), '-m',
                        str(month), '-d', str(day), '-y', str(year), '-H', str(hour)]
                print('Running fuzzy mode\nsearching for baby name for surname {0}, gender: {1}, date of birth: {2}-{3}-{4}' \
                      .format(args[1], args[3], args[5], args[7], args[9]))
            EZName.main(args)   # run the main program
            print('Done!')
        else:
            print('Error! Canvas is not initialized!')
            return

    def runWithoutConfig(self):
        pass

    def testRun(self):
        args = ['-s', '李', '-g', 'M', '-y', '2020', '-m', '7', '-d', '3', '-H', '10']
        print('Running test mode\nsearching baby name for surname {0}, gender: {1}, date of birth: {2}-{3}-{4}' \
              .format(args[1], args[3], args[7], args[9], args[5]))
        EZName.main(args)
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


class Canvas:

    def __init__(self, master):

        self.master = master
        self.calIcon = tk.PhotoImage(file='resource/cal_icon_2.png').subsample(10)

        self.labelDate = tk.Label(master, font=('Arial', 14, 'bold'), text='Pick your due date')
        self.labelDate.grid(column=0, row=1, pady=10)

        self.labelMonth = tk.Label(master, text='Month')
        self.labelMonth.grid(column=0, row=2, sticky=tk.W)
        self.labelDay = tk.Label(master, text='Day')
        self.labelDay.grid(column=1, row=2, sticky=tk.W)
        self.labelYear = tk.Label(master, text='Year')
        self.labelYear.grid(column=2, row=2, sticky=tk.W)
        self.labelCalendar = tk.Label(master, text='Calendar')
        self.labelCalendar.grid(column=3, row=2, sticky=tk.W)
        self.labelHour = tk.Label(master, text='Hour (Optional)')
        self.labelHour.grid(column=4, row=2, sticky=tk.W)

        # add a combobox for month selection
        self.months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                  "November", "December"]
        self.comboMonth = ttk.Combobox(master, height=10, width=7, values=self.months)
        self.comboMonth.grid(column=0, row=3, sticky=tk.W)
        self.comboMonth.current(0)

        # add a combobox for year selection
        self.today = datetime.date.today()
        years = [i for i in range(self.today.year, self.today.year + 5)]
        self.comboYear = ttk.Combobox(master, height=20, width=5, values=years)
        self.comboYear.grid(column=2, row=3, sticky=tk.W)
        self.comboYear.current(0)

        # add a combobox for day selection
        monthdays = monthrange(int(self.comboYear.get()), self.months.index(self.comboMonth.get()) + 1)[1]
        self.comboDay = ttk.Combobox(master, height=20, width=5, values=[i for i in range(1, monthdays + 1)])
        self.comboDay.grid(column=1, row=3, sticky=tk.W)
        self.comboDay.current(0)

        # add a combobox for hour selection
        self.comboHour = ttk.Combobox(master, height=20, width=5, values=[i for i in range(0, 24)], state='disabled')
        self.comboHour.grid(column=4, row=3)
        self.comboHour.current(0)

        # add a radiobutton for lookup mode
        self.lookupMode = tk.IntVar(master, 1)
        lookupModeValues = {"Fuzzy Mode": 1, "Exact Mode": 2}
        btnNum = 0
        for (text, value) in lookupModeValues.items():
            self.btnModeSelect = tk.Radiobutton(master, text=text, variable=self.lookupMode, value=value, command=self.selectMode)
            self.btnModeSelect.grid(column=5, row=3 + btnNum)
            btnNum += 1

        self.comboMonth.bind("<<ComboboxSelected>>", self.monthSelectionCallback)
        self.comboDay.bind("<<ComboboxSelected>>", self.daySelectionCallback)
        self.comboYear.bind("<<ComboboxSelected>>", self.yearSelectionCallback)
        self.comboHour.bind("<<ComboboxSelected>>", self.hourSelectionCallback)
        self.calBtn = ttk.Button(master, image=self.calIcon, command=self.popupCal, width=1)
        self.calBtn.grid(column=3, row=3)

        # add a label and textbox for last name entry
        self.lastNameLabel = tk.Label(master, font=('Arial', 14, 'bold'), text='Your last name')
        self.lastNameLabel.grid(column=0, row=5, pady=10)
        self.lastNameEntry = tk.Entry(master, width=5)
        self.lastNameEntry.grid(column=1, row=5)

        # add a label and combobox for baby gender
        self.genderLabel = tk.Label(master, text='Gender')
        self.genderLabel.grid(column=2, row=5)
        self.comboGender = ttk.Combobox(master, height=2, width=2, values=['M', 'F'])
        self.comboGender.grid(column=3, row=5)
        self.comboGender.set('M')


        # add a checkbox to indicate if enable name scoring
        self.enableNameScoring = tk.BooleanVar(master, True)
        self.chkBtn = ttk.Checkbutton(master, variable=self.enableNameScoring, onvalue=True, offvalue=False,
                                      text='Get name score?', command=self.printNameScore)
        self.chkBtn.grid(column=0, row=6, pady=10)

        # add the run button
        self.style = ttk.Style()
        self.style.configure('my.TButton', font=('Arial', 16, 'bold'), foreground='green', background='black')
        self.runBtn = ttk.Button(master, text='Find Names', style='my.TButton', width=10,
                                 command=self.findNames)
        self.runBtn.grid(column=1, row=6)

    def findNames(self):
        lastName = self.lastNameEntry.get()
        if not lastName:
            print('last name is missing!')
            return
        month = self.months.index(self.comboMonth.get()) + 1
        day = self.comboDay.get()
        year = self.comboYear.get()
        gender = self.comboGender.get()
        if self.comboHour['state'].string == 'normal':
            hour = self.comboHour.get()
            args = ['-s', str(lastName), '-g', str(gender), '-m',
                    str(month), '-d', str(day), '-y', str(year), '-H', str(hour)]
            print('Running exact mode\nsearching baby name for surname {0}, gender: {1} date of birth: {2}-{3}-{4}, hour: {5}' \
                .format(args[1], args[3], args[5], args[7], args[9], args[11]))
        else:
            hour = None
            args = ['-s', str(lastName), '-g', str(gender), '-m',
                    str(month), '-d', str(day), '-y', str(year), '-H', str(hour)]
            print('Running fuzzy mode\nsearching for baby name for surname {0}, gender: {1}, date of birth: {2}-{3}-{4}' \
                  .format(args[1], args[3], args[5], args[7], args[9]))
        EZName.main(args)  # run the main program
        print('Done!')

    def printNameScore(self):
        print(self.enableNameScoring.get())
        #print(self.lastNameEntry.get())


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


if __name__ == "__main__":
    app = tk.Tk()
    app.geometry('600x400')
    app.title('EZName v1.0')
    menu = Menu(app)
    canvas = Canvas(app)
    menu.bindCanvasObj(canvas) # bind the canvas object to menu object in order to update the user selection
    app.mainloop()