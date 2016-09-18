from tkinter import *

class Application(object):
    def __init__(self):
        self.top = Tk()
        self.top.title('Hello')
        self.CreateWidgets()
        self.top.mainloop()

    def CreateWidgets(self):
        self.userText = Entry(self.top)
        self.userText.grid(row=0, column=0)

        self.searchButton = Button(self.top, text=u'查询', command=self.Search)
        self.searchButton.grid(row=0, column=1)

        self.translateText = Text(self.top)
        self.translateText.grid(row=1, column=0, columnspan=2)

    def Search(self):
        self.translateText.delete(0.0, END)
        self.translateText.insert(0.0, 'Hello')

app = Application()