from tkcalendar import Calendar, DateEntry
try:
    from tkinter import ttk   # Python3
    import tkinter as tk
except ImportError:
    import Tkinter as tk    # Python 2
    import ttk
import datetime
from calendar import monthrange


class Canvas:

    def __init__(self, master):

        self.calIcon = tk.PhotoImage(file='resource/cal_icon_2.png').subsample(10)

        self.labelDate = tk.Label(app, font=('Arial', 14, 'bold'), text='Pick your due date')
        self.labelDate.grid(column=0, row=1, pady=20)

        self.labelMonth = tk.Label(app, text='Month')
        self.labelMonth.grid(column=0, row=2)
        self.labelDay = tk.Label(app, text='Day')
        self.labelDay.grid(column=1, row=2)
        self.labelYear = tk.Label(app, text='Year')
        self.labelYear.grid(column=2, row=2)
        self.labelYear = tk.Label(app, text='Calendar')
        self.labelYear.grid(column=3, row=2)
        self.labelHour = tk.Label(app, text='Hour (Optional)')
        self.labelHour.grid(column=4, row=2)

        # add a combobox for month selection
        self.months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                  "November", "December"]
        self.comboMonth = ttk.Combobox(app, height=10, width=10, values=self.months)
        self.comboMonth.grid(column=0, row=3, padx=5)
        self.comboMonth.current(0)

        # add a combobox for year selection
        self.today = datetime.date.today()
        years = [i for i in range(self.today.year, self.today.year + 5)]
        self.comboYear = ttk.Combobox(app, height=20, width=5, values=years)
        self.comboYear.grid(column=2, row=3)
        self.comboYear.current(0)

        # add a combobox for day selection
        monthdays = monthrange(int(self.comboYear.get()), self.months.index(self.comboMonth.get()) + 1)[1]
        self.comboDay = ttk.Combobox(app, height=20, width=3, values=[i for i in range(1, monthdays + 1)])
        self.comboDay.grid(column=1, row=3, padx=10)
        self.comboDay.current(0)

        # add a combobox for hour selection
        self.comboHour = ttk.Combobox(app, height=20, width=5, values=[i for i in range(0, 24)], state='disabled')
        self.comboHour.grid(column=4, row=3, padx=10)
        self.comboHour.current(0)

        # add a radiobutton for lookup mode
        self.lookupMode = tk.IntVar(app, 1)
        lookupModeValues = {"Fuzzy Mode": 1, "Exact Mode": 2}
        btnNum = 0
        for (text, value) in lookupModeValues.items():
            self.btnModeSelect = tk.Radiobutton(app, text=text, variable=self.lookupMode, value=value, command=self.selectMode)
            self.btnModeSelect.grid(column=5, row=3 + btnNum, padx=5)
            btnNum += 1

        self.comboMonth.bind("<<ComboboxSelected>>", self.monthSelectionCallback)
        self.comboDay.bind("<<ComboboxSelected>>", self.daySelectionCallback)
        self.comboYear.bind("<<ComboboxSelected>>", self.yearSelectionCallback)
        self.calBtn = ttk.Button(master, image=self.calIcon, command=self.popupCal, width=1).grid(column=3, row=3)


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
            self.comboMonth.set(sel_date.month)
            self.comboDay.set(sel_date.day)
        mindate = self.today
        maxdate = self.today + datetime.timedelta(weeks=300)
        top = tk.Toplevel(app)
        self.cal = Calendar(top, font="Arial 14", selectmode='day', locale='en_US',
                       mindate=mindate, maxdate=maxdate, disabledforeground='red',
                       cursor="hand1", year=self.today.year, month=self.today.month, day=self.today.day)
        self.cal.pack(fill="both", expand=True)
        ttk.Button(top, text='OK', command=updateDate).pack()


if __name__ == "__main__":
    app = tk.Tk()
    app.geometry('600x400')
    app.title('EZName v1.0')
    canvas = Canvas(app)
    app.mainloop()