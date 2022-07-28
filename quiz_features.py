import sqlite3
from random import sample
from tkinter import *
from tkinter.ttk import Treeview

from question_answers import Question, Answer


class App(Tk):
    """The main app frame which is inheriting from the tkinter object Tk so it behaves as our main window"""
    def __init__(self):
        super().__init__()
        self.geometry('750x350')
        self.title('Quiz App')
        modules_page = Modules(self)
        modules_page.pack()

    @staticmethod
    def test_modules():
        con = sqlite3.connect('question_bank.db')
        cur = con.cursor()
        con.commit()
        con.close()

    @staticmethod
    def create_db():
        """A static method to create a database, we use if not exists in the sqlite statements so in case if the table
        already exists the code will simply not create a new table. The tables we have used are Modules, Questions,
        Answers and Results """
        modules = sqlite3.connect('question_bank.db')
        m = modules.cursor()
        m.execute('''CREATE TABLE IF NOT EXISTS modules
                 (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                 Name TEXT NOT NULL,
                 Code INTEGER NOT NULL)''')
        modules.commit()
        modules.close()

        questions = sqlite3.connect('question_bank.db')
        q = questions.cursor()
        q.execute('''CREATE TABLE IF NOT EXISTS Questions
                 (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                 Question TEXT NOT NULL,
                 Type TEXT NOT NULL,
                 Mark INTEGER NOT NULL,
                 Module_ID INT NOT NULL,
                 Number INTEGER DEFAULT 0,
                 FOREIGN KEY(Module_ID) REFERENCES modules(ID))''')
        questions.commit()
        questions.close()

        answers = sqlite3.connect('question_bank.db')
        a = answers.cursor()
        a.execute('''CREATE TABLE IF NOT EXISTS Answers
                 (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                 Answer TEXT NOT NULL,
                 Description TEXT,
                 Is_Right INT NOT NULL,
                 Question_ID INT NOT NULL,
                 FOREIGN KEY(Question_ID) REFERENCES Questions(ID))''')
        answers.commit()
        answers.execute("""CREATE TABLE results(
        id INTEGER PRIMARY KEY,
        module_id INTEGER,
        number_of_questions integer,
        number_of_correct_answers INTEGER,
        time_taken TEXT                                                 
        )""")


class Receptor:
    """A class whose sole purpose is to communicate between various classes we have used. We use this class to
    communicate the main window root to other classes and the selected module id from the review between different
    classes """

    def __init__(self):
        self.root = None
        self.id_m = None


receptor = Receptor()


class TextLabel(Frame):
    """A class to show the text label for achievements"""

    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.btn = Button(self, text="Achievements", command=self.navigate)
        self.btn.pack()

    def navigate(self):
        """A function to navigate to the main modules page after the back button is clicked"""
        Modules(self).pack()
        self.pack_forget()


class Modules(Frame):
    """The main modules frame class where the list of modules is dynamically displayed from the database which is
    linked to the administrative features. From here the user could select a module and then launch the quiz for it
    and get the relevant report and achievements. The class is inheriting from the tkinter object Frame."""

    def __init__(self, master):
        Frame.__init__(self, master)
        self.tree = Treeview(self, columns=['name'], show='headings')
        self.tree.pack(fill=X, expand=True)
        self.tree.heading('name', text='Module Name')
        self.insert_modules()
        self.btn = Button(self, text="Achievement", command=self.navigate)
        self.btn.pack()
        self.btn1 = Button(self, text="Take", command=self.take)
        self.btn1.pack()
        self.btn2 = Button(self, text="Report", command=self.report)
        self.btn2.pack()
        self.pack(fill=X, expand=True)

    def report(self):
        """A function to configure the report toplevel"""
        report_toplevel = Toplevel(self)
        con = sqlite3.connect('question_bank.db')
        cur = con.cursor()
        self.selected_module = (self.tree.item(self.tree.focus())['values'][0])
        query = cur.execute('''SELECT ID FROM modules where Name = ?''', (self.selected_module,))
        self.selected_module_id = query.fetchone()
        receptor.id_m = self.selected_module_id[0]
        Report(report_toplevel).mainloop()
        self.pack_forget()

    def navigate(self):
        """A function to open the achievements page"""
        Achievements(receptor.root).pack()
        self.pack_forget()

    def take(self):
        """A function to launch the quiz for a selected module"""
        module = self.get_selected_module()
        quiz = Quiz(receptor.root, module)
        quiz.pack()
        self.pack_forget()

    def get_selected_module(self):
        """A function to get the selected module from the treeview and return it so that it can be further used to
        display objects only related to the selected module """
        item = self.tree.selection()[0]
        item = self.tree.item(item)['values']
        item = item[0]
        return item

    def insert_modules(self):
        """A function to fill the TreeView with rows from our database"""
        modules = Modules.get_modules()
        for module in modules:
            self.tree.insert('', END, values=module)

    @staticmethod
    def get_modules():
        """A function to get the modules from the database and return them """
        con = sqlite3.connect('question_bank.db')
        cur = con.cursor()
        cur.execute("SELECT Name FROM modules")
        con.commit()
        modules = cur.fetchall()
        con.close()
        return modules


class Quiz(Frame):
    """A frame class for the quiz which runs after a module is selected and the user clicks on "Take", this class
    displays random 5 questions out of the database and the answers relevant to it. After the quiz is finished it will
    also show the score achieved. This class inherits from the tkinter object Frame. """
    def __init__(self, master, module):
        Frame.__init__(self, master)
        self.master = master
        self.module = module
        self.master.title(self.module)

        self.descriptions = []
        self.questions = []
        self.index = 0
        self.result = 0

        for question in self.get_questions():
            ques = self.get_questions_as_objects(question)
            self.questions.append(ques)
        self.questions = sample(self.questions, 5)
        self.page = InsideQuiz(self, self.questions[self.index], self.module)
        self.page.pack()

    def get_questions(self):
        """A function to get the questions from the database and return it"""
        con = sqlite3.connect('question_bank.db')
        cur = con.cursor()
        cur.execute("""SELECT Question FROM questions WHERE module_id=(SELECT ID FROM modules WHERE name=?)""",
                    [self.module])
        con.commit()
        questions = cur.fetchall()
        con.close()
        return questions

    def get_questions_as_objects(self, question):
        con = sqlite3.connect('question_bank.db')
        cur = con.cursor()
        cur.execute("""SELECT Answer, description, Is_Right FROM Answers WHERE question_id=
        (SELECT id FROM questions WHERE question=?)""", question)
        con.commit()
        answers = []
        results = cur.fetchall()

        for result in results:
            ans = Answer(result[0], result[1], result[2])
            answers.append(ans)
        con.close()

        return Question(question, answers)

    def grade(self, quest, option):
        """A function to grade the quiz the user takes. It will return 1 if the option selected by user is correct and 0 if the answer is wrong."""
        correct_answer_list = []
        con = sqlite3.connect('question_bank.db')
        cur = con.cursor()
        query = cur.execute('''SELECT ID FROM questions WHERE Question = ?''',
                            (quest,))
        self.question_id = query.fetchone()
        query = cur.execute('''SELECT Answer FROM answers WHERE Question_ID = ? AND Is_Right = 1''',
                            (self.question_id[0],))
        correct_answers = query.fetchall()
        for i in range(len(correct_answers)):
            correct_answer_list.append(correct_answers[i][0])
        if option in correct_answer_list:
            return 1
        else:
            return 0

    def next(self, quest, option, is_right, desc):
        """A function to simply switch to the next question"""
        con = sqlite3.connect('question_bank.db')
        cur = con.cursor()
        cur.execute('''UPDATE Questions SET Number = Number + 1 WHERE Question = ?''', (quest,))
        con.commit()
        print(self.grade(quest, option))
        self.result += self.grade(quest, option)
        self.descriptions.append(desc)
        if self.index == len(self.questions) - 1:
            self.go_to_result_page()
        else:
            print(is_right)
            self.page.destroy()
            self.index += 1
            self.page = InsideQuiz(self, self.questions[self.index], self.module)
            self.page.pack()

    def go_to_result_page(self):
        """A function to switch the frame to the results frame where the score achieved would be displayed"""
        page = Result(receptor.root, self.result, len(self.questions), self.module)
        page.pack()
        self.pack_forget()


class Report(Frame):
    """A frame class to display the report information for the selected module which would display a treeview with
    the questions and the number of times the question was asked in a quiz. It also displays the max score,
    lowest score and the average score achieved. """
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        con = sqlite3.connect('question_bank.db')
        cur = con.cursor()
        self.tree = Treeview(master, columns=['question', 'number'], show='headings')
        self.tree.heading('question', text='Question')
        self.tree.heading('number', text='Number of times asked')
        self.tree.pack()
        self.btn1 = Button(master, text="Back", command=self.back)
        self.btn1.pack()
        max_score_query = cur.execute('''SELECT MAX(number_of_correct_answers) FROM results WHERE Module_ID=?''',
                                      (receptor.id_m,))
        max_score = max_score_query.fetchone()[0]
        low_score_query = cur.execute('''SELECT MIN(number_of_correct_answers) FROM results WHERE Module_ID=?''',
                                      (receptor.id_m,))
        low_score = low_score_query.fetchone()[0]
        print(max_score)
        print(low_score)
        try:
            avg_score = (max_score + low_score) / 2
        except:
            avg_score = low_score

        self.max_score_label = Label(master, text=f'The highest score achieved for selected module: {max_score}')
        self.max_score_label.pack()
        self.low_score_label = Label(master, text=f'The lowest score achieved for selected module: {low_score}')
        self.low_score_label.pack()
        self.average_score_label = Label(master, text=f'The average score achieved for selected module: {avg_score}')
        self.average_score_label.pack()
        self.update_tree()

    def back(self):
        """A function to destroy the report TopLevel"""
        self.master.destroy()

    def update_tree(self):
        """A function to populate the TreeView with columns from database"""
        con = sqlite3.connect('question_bank.db')
        cur = con.cursor()
        self.tree.delete(*self.tree.get_children())
        cur.execute('''SELECT Question,Number FROM Questions WHERE MODULE_ID=(?)''', (receptor.id_m,))
        rows = cur.fetchall()
        for row in rows:
            self.tree.insert("", END, values=row)


class InsideQuiz(Frame):
    """A frame class to configure and display the objects inside a quiz like the question, relevant options and a
    button to navigate between questions and finally submit """
    def __init__(self, master, question, module):
        Frame.__init__(self, master)
        self.master = master
        self.question = question

        # To replace {} brackets
        quest = question.question[0]
        quest = quest.replace('{', '')
        quest = quest.replace('}', '')

        lbl = Label(self, text=quest)
        lbl.pack()

        for answer in question.answers:
            self.mybutton = Button(self, text=answer.answer,
                                   command=lambda button_text=answer.answer: self.next(quest, button_text,
                                                                                       answer.isright,
                                                                                       answer.description))
            self.mybutton.pack()

    def next(self, quest, button_text, is_right, desc):
        """A function to go the next question"""
        print(button_text)
        self.master.next(quest, button_text, is_right, desc)
        self.pack_forget()


class Result(Frame):
    """A frame class to display the result achieved from the quiz taken. It displays the score and an option to exit
    to the main module page. This class inherits from the tkinter object Frame """
    def __init__(self, master, results, number_of_questions, module):
        Frame.__init__(self, master)
        self.module = module
        self.master = master
        txt = "Your score is: {} of {}".format(results, number_of_questions)
        label = Label(self, text=txt)
        label.pack()

        exit_btn = Button(self, text='Exit', command=self.exit)
        exit_btn.pack()
        Result.insert_result(self.module, number_of_questions, results)

    def exit(self):
        """A function to exit the results and go back to the main modules page"""
        module = Modules(receptor.root)
        module.pack(fill=X, expand=True)
        self.pack_forget()

    @staticmethod
    def insert_result(module, number_of_questions, number_of_correct_answers):
        """A function to push the results into the database."""
        con = sqlite3.connect('question_bank.db')
        cur = con.cursor()
        cur.execute("INSERT INTO results(module_id, number_of_questions, number_of_correct_answers, time_taken) VALUES("
                    ""
                    "(SELECT id FROM modules WHERE name=?),?,?, DATETIME('now', 'localtime'))",
                    [module, number_of_questions, number_of_correct_answers])
        con.commit()
        con.close()


class Achievements(Frame):
    """A frame class to display the Achievements of the user which contains the previous score achieved, the date and
    time the quiz was taken on and the module name """
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.tree = Treeview(self, columns=['result', 'date', 'module'], show='headings')
        self.tree.heading('result', text='Results')
        self.tree.heading('date', text='Date/Time')
        self.tree.heading('module', text='Module')
        self.tree.pack()

        for result in Achievements.get_results():
            module = result[0]
            module = Achievements.get_module_from_id(module)
            carry = "{} of {}".format(result[2], result[1])
            self.tree.insert('', END, values=[carry, result[3], module])
        go_back_btn = Button(self, text="Go Back", command=self.go_back)
        go_back_btn.pack()

    def go_back(self):
        """A function to go back to the main modules page"""
        Modules(receptor.root).pack(fill=X, expand=True)
        self.pack_forget()

    @staticmethod
    def get_results():
        """A function to fetch the results from the database and return them"""
        con = sqlite3.connect('question_bank.db')
        cur = con.cursor()
        cur.execute("SELECT module_id, number_of_questions, number_of_correct_answers, time_taken FROM results")
        results = cur.fetchall()
        con.commit()
        con.close()
        return results

    @staticmethod
    def get_module_from_id(module_id):
        """"""
        con = sqlite3.connect('question_bank.db')
        cur = con.cursor()
        cur.execute("SELECT name FROM modules WHERE id=?", [module_id])
        name = cur.fetchone()
        name = name[0]
        con.commit()
        con.close()
        return name


class Launch:
    """A simple class made to launch the main application so that it can be launched from our menu"""
    def launch(self):
        root = App()
        receptor.root = root
        mainloop()


launch = Launch()
if __name__ == '__main__':
    launch.launch()
