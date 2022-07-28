import admin_features
import quiz_features
from tkinter import *

window = Tk()
window.geometry('700x300')
window.rowconfigure([0, 1], weight=1)
window.columnconfigure([0], weight=1)
admin_button = Button(window, text="Administrative Functions", command=admin_features.launch.splash)
admin_button.grid(row=0, column=0, sticky='news')
quiz_button = Button(window, text="Take a Quiz", command=quiz_features.launch.launch)
quiz_button.grid(row=1, column=0, sticky='news')

window.mainloop()
