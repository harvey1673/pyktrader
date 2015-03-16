import Tkinter
import tkFont as font

class Gui(Tkinter.Tk):      
    def __init__(self, agent):
        Tkinter.Tk.__init__(self)

        self.logic = logic

        self.geometry("370x170")
        self.resizable(width=False, height=False)

        rock_button = Tkinter.Button(self, text="Rock", command=self.rock_clicked)
        rock_button.place(width=100, height=30, x=10, y=30)

        paper_button = Tkinter.Button(self, text="Paper", command=self.paper_clicked)
        paper_button.place(width=100, height=30, x=10, y=70)

        scissors_button = Tkinter.Button(self, text="Scissors", command=self.scissors_clicked)
        scissors_button.place(width=100, height=30, x=10, y=110)

        score_font = font.Font(family="Helvetica", size=20)

        own_score_lbl = Tkinter.Label(self, text="0", relief=Tkinter.RIDGE, font=score_font)
        own_score_lbl.place(width=50, height=110, x=120, y=30)

        ai_score_lbl = Tkinter.Label(self, text="0", relief=Tkinter.RIDGE, font=score_font)
        ai_score_lbl.place(width=50, height=110, x=200, y=30)

        ai_choice = Tkinter.Label(self, relief=Tkinter.RIDGE)
        ai_choice.place(width=100, height=110, x=260, y=30)

        self.render_title()

    def render_title(self):
        logic = self.logic
        templ = "Rock({logic.rock_counter}), Paper({logic.paper_counter}), Scissors({logic.scissors_counter})"
        title = templ.format(logic=logic)
        self.title(title)

    def rock_clicked(self):
        self.logic.play_rock()
        self.render_title()

    def paper_clicked(self):
        self.logic.play_paper()
        self.render_title()

    def scissors_clicked(self):
        self.logic.play_scissors()
        self.render_title()

import Tkinter as tk

class Demo1:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.button1 = tk.Button(self.frame, text = 'New Window', width = 25, command = self.new_window)
        self.button1.pack()
        self.frame.pack()
    def new_window(self):
        self.newWindow = tk.Toplevel(self.master)
        self.app = Demo2(self.newWindow)

class Demo2:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.quitButton = tk.Button(self.frame, text = 'Quit', width = 25, command = self.close_windows)
        self.quitButton.pack()
        self.frame.pack()
    def close_windows(self):
        self.master.destroy()

def main(): 
    root = tk.Tk()
    app = Demo1(root)
    root.mainloop()