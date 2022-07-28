"""Our GUI is based on Tkinter and our database is made with SQLite3.
    We import ttk and messagebox to have additional GUI features."""
import logging
from tkinter import *
from tkinter import ttk, messagebox
import sqlite3

"""We are using logging to log the errors (if any) to a log file named app.log. In reality there is no chance of 
errors as this code has been thoroughly tested but consider this an additional feature we decided to implement just 
in case the user faces an issue. """

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

"""Here we connect our Python code with the SQLite3 database and declare the cursors."""
"""Repair this (DATABASE)"""

"""In these sqlite3 commands we are checking everytime if the table exists instead of just creating the table once 
and not including those commands at all because in case the user accidentally deletes the database files, they won't 
face any issues as this code will automatically create the database files again."""

conn = sqlite3.connect('question_bank.db', timeout=10)
curr = conn.cursor()


class TreeView(Frame):
    """We are inheriting the tkinter object, Frame here so that we can treat this class as the object itself when it
    comes to creating the UI for our app.

    One could say that we are using polymorphism here as we are using the same class to create three different
    types of TreeViews and have a search function in this class which work with all different TreeViews. """

    def __init__(self, master, columns):
        Frame.__init__(self, master)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(self, column=columns, show='headings')
        self.tree.grid(row=0, column=0, sticky='NEWS')

    def search(self, query):

        """This function is the core of our search functionality. It takes and stores the user query from the search
        entry to a private? variable and then iterates through all the children in the TreeView and tries to compare
        the search query in lowercase with all relevant TreeView children values in lowercase. If it finds a match,
        it will append the value of that child to a list we name selections. Then we select the items in selections
        visually in our TreeView to show the results to the user. """

        _selections = []
        for child in self.tree.get_children():
            if query.lower() in self.tree.item(child)['values'][1].lower():
                _selections.append(child)

            if query in str(self.tree.item(child)['values'][0]):
                _selections.append(child)
        self.tree.selection_set(_selections)
        _selections = []


class MainFrame(Tk):
    """We are inheriting from the tkinter object, TK here so that we can treat this class as our main window."""

    def __init__(self):
        Tk.__init__(self)
        self._frame = None
        self.switch_frame(ModuleClass)

    def switch_frame(self, frame_class):
        """We are using polymorphism here to switch between different frame classes as it's the same method but
        different frames.

        Function to switch between various class frames in our project like ModuleClass, QuestionClass and
        AnswerClass. The function takes in a frame class as a parameter and then grid places it. This function can be
        taken as an example to show polymorphism in our code as we are using the same function to display different
        classes.

        We are passing self as the master."""

        _new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = _new_frame
        self._frame.grid(row=0, column=0, sticky='nsew')


class Receptor:
    """A static class used for communicating between various classes."""

    def __init__(self):
        self.id_m = None
        self.id_q = None


"""Making an instance of the Receptor class"""
Receptor = Receptor()


class ModuleClass(Frame):
    """A class for the modules page which inherits from the tkinter object, Frame. This class inherits from Frame so
    that it can be used to switch frames using the MainFrame function switch_frame. In the __init__ constructor we
    are declaring our module TreeView and the grid placement of this frame class. We decided to declare the
    individual frames inside different methods so that they don't get created unless the user wants to create them as
    the __init__ constructor would create objects declared inside of it as soon as the class is called. """

    def __init__(self, master):
        Frame.__init__(self, master)
        rows = curr.execute('''SELECT ID, Name, Code FROM Modules''').fetchall()

        """TreeView variables"""
        columns = ("column1", "column2", "column3")
        self.module_tree = TreeView(self, columns)
        self.module_tree.tree.heading('#1', text='Module Code')
        self.module_tree.tree.heading('#2', text='Module Name')
        self.module_tree.tree.heading('#3', text="ID")
        self.module_tree.tree["displaycolumns"] = ("0", "1")
        self.update_module_tree()
        self.module_tree.grid(row=0, column=0, columnspan=4, sticky='nsew')
        self.module_tree.tree.bind("<Double-1>", self.module_switch_frame)

        """Module frame configuration."""
        self.grid_columnconfigure([0, 1, 2, 3], weight=1)
        self.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        """Add module button configuration."""
        self.add_module_frame = Frame(self)
        self._add_module_button = Button(self, text="Add module",
                                         command=lambda: [self.forget_bottom_frames(), self.add_module()])
        self._add_module_button.grid(row=1, column=0, pady=20, sticky='ew')

        """Search button/frame configuration"""
        self.search_module_frame = Frame(self)
        self.search_button = Button(self, text="search", command=self.search_view)
        self.search_button.grid(row=1, column=3, pady=20, sticky='ew')
        self._search_entry_label = None
        self.search_entry = None
        self.search_button_iframe = None
        self._search_quit_button = None

        """Edit module configuration"""
        self.edit_module_frame = Frame(self)
        self._edit_module_button = Button(self, text="Edit module", command=lambda: [self.forget_bottom_frames(),
                                                                                     self.check_module_focus(
                                                                                         self.edit_module)])
        self._edit_module_button.grid(row=1, column=1, pady=20, sticky='ew')

        """Delete module configuration"""
        self._delete_module_button = Button(self, text="Delete module",
                                            command=lambda: [self.check_module_focus(self.delete_module)])
        self._delete_module_button.grid(row=1, column=2, pady=20, sticky='ew')

        """Extras"""
        self.selected_module_id = None

    def check_module_focus(self, inspector):

        """This function checks if a child in the current TreeView is selected, if it is selected it will proceed
        with executing a function else it will display an error asking the user to select a module from the TreeView.
        """

        if self.module_tree.tree.focus() != "":
            inspector()
        else:
            messagebox.showinfo(title="Error", message="Please select a module")

    def module_switch_frame(self, _event):

        """This function sets the selected_module_id to the current selected module id in the TreeView and then
        passes the value on to a receptor class which will then be accessed by the QuestionClass to display questions
        which are only related to the module that we have selected."""
        try:
            self.selected_module_id = (self.module_tree.tree.item(self.module_tree.tree.focus())['values'][2])
            Receptor.id_m = self.selected_module_id
            self.master.switch_frame(QuestionClass)
        except Exception as e:
            logging.error(e)

    def forget_bottom_frames(self):
        """A basic function to grid_forget add, edit and search module frames so that they never overlap."""
        try:
            self.add_module_frame.grid_forget()
            self.edit_module_frame.grid_forget()
            self.search_module_frame.grid_forget()
        except Exception as e:
            logging.error(e)

    def search_view(self):
        """A function to launch and place the search functionality for modules."""
        try:
            self.forget_bottom_frames()
            self._search_entry_label = Label(self.search_module_frame, text="Search")
            self._search_entry_label.grid(row=0, column=0, columnspan=2)
            self.search_entry = Entry(self.search_module_frame)
            self.search_entry.grid(row=1, column=0, columnspan=2)
            self.search_button_iframe = Button(self.search_module_frame, text="Search",
                                               command=lambda: [self.module_tree.search(self.search_entry.get())])
            self.search_button_iframe.grid(row=2, column=0, pady=20, sticky='w')
            self.search_button = Button(self, text="search", command=self.search_view)
            self.search_button.grid(row=1, column=3, pady=20, sticky='ew')
            self._search_quit_button = Button(self.search_module_frame, text="Quit", command=self.forget_bottom_frames)
            self._search_quit_button.grid(row=2, column=1, sticky='e', pady=20)
            self.search_module_frame.grid(row=2, column=1, columnspan=2)
        except Exception as e:
            logging.error(e)

    def edit_module(self):

        """Function to implement and add the elements required for editing a module. The function automatically grabs
        the values of the selected child and inserts it into the entry boxes so that it's easier for the user to
        edit. After the user clicks submit, we check if there's a module."""

        self.edit_module_frame.grid(row=2, column=0)

        lbl_1 = Label(self.edit_module_frame, text="New name")
        lbl_1.grid(row=0, column=1)
        name = Entry(self.edit_module_frame)
        name.grid(row=1, column=1)
        lbl_2 = Label(self.edit_module_frame, text="New code")
        lbl_2.grid(row=2, column=1)
        code = Entry(self.edit_module_frame)
        code.grid(row=3, column=1)
        code.insert(0, self.module_tree.tree.item(self.module_tree.tree.focus())['values'][0])
        name.insert(0, self.module_tree.tree.item(self.module_tree.tree.focus())['values'][1])
        edit_module_button = Button(self.edit_module_frame, text="Submit",
                                    command=lambda: [self.edit_module_database(name.get(), code.get()),
                                                     self.edit_module_frame.grid_forget()])
        edit_module_button.grid(row=4, column=1, pady=20, sticky='w')
        quit_button = Button(self.edit_module_frame, text="Quit", command=self.edit_module_frame.grid_forget)
        quit_button.grid(row=4, column=1, sticky='e', pady=20)
        self.edit_module_frame.grid(row=2, columnspan=4)

    def update_module_tree(self):

        """Function to refresh the list of all children in our module TreeView. The function first deletes all the
        children currently present in our TreeView and then fetches it again from the database and inserts it into
        the TreeView."""
        try:
            self.module_tree.tree.delete(*self.module_tree.tree.get_children())
            curr.execute('''SELECT code,name,ID FROM modules''')
            rows = curr.fetchall()
            for row in rows:
                self.module_tree.tree.insert("", END, values=row)
        except Exception as e:
            messagebox.showerror(title="Error", message=e)

    def edit_module_database(self, name, code):

        """Function which is used to edit the Modules database using the name and code provided from the user. """

        try:
            id_q = (self.module_tree.tree.item(self.module_tree.tree.focus())['values'][2])
            if name == "" or code == "":
                messagebox.showinfo("Invalid input", "Module name and code fields can not be empty.")
            else:
                message_edit = messagebox.askyesno("Confirmation", "Do you want to permanently update this question?",
                                                   parent=self.edit_module_frame)
                if message_edit > 0:
                    if code == str(self.module_tree.tree.item(self.module_tree.tree.focus())['values'][0]):
                        curr.execute('''UPDATE Modules SET name = ? , code = ? WHERE ID = ?''',
                                     (name, code, id_q))
                        conn.commit()
                        self.update_module_tree()
                    else:
                        if self.check_module_duplicate(code) == 1:
                            messagebox.showinfo(message="Module code already exists in database")
                        else:
                            curr.execute('''UPDATE Modules SET name = ? , code = ? WHERE ID = ?''',
                                         (name, code, id_q))
                            conn.commit()
                            self.update_module_tree()
        except Exception as e:
            print(e)

    def delete_module(self):

        """A function to delete a module selected in the TreeView by the user. The function also asks the user to
        confirm if they want to delete a selected module using the messagebox module. Deleting a module will also
        delete the questions and answers related to it."""

        try:
            id_m = (self.module_tree.tree.item(self.module_tree.tree.focus())['values'][2])
            message_delete = messagebox.askyesno("Confirmation", "Do you want to permanently delete this module?")
            if message_delete > 0:
                curr.execute('''DELETE FROM Modules WHERE ID=(?)''', (id_m,))
                curr.execute('''DELETE FROM Questions WHERE Module_ID=(?)''', (id_m,))

                conn.commit()
                self.update_module_tree()

        except Exception as e:
            messagebox.showerror(title="Error", message=e)

    @staticmethod
    def check_module_duplicate(code):

        """This function checks for module code duplicates. We execute and check if there are any rows with the same
        module code as the query and store that value in response. If fetched is not none, there are duplicates and
        hence we can execute appropriate code dependent on the value of fetched."""

        response = conn.execute("SELECT EXISTS(SELECT 1 FROM Modules WHERE code=?)", (code,))
        fetched = response.fetchone()[0]
        return fetched

    def add_module(self):

        """Function containing code specific to adding module to the database."""
        """The sql statement below would ensure the autoincrement ID gets set properly instead of having ghost value 
        rows. We do this so that the value does not overflow in the far future. """
        curr.execute('''UPDATE sqlite_sequence SET seq = (SELECT MAX(ID) FROM modules) WHERE name="modules"''')
        self.add_module_frame.grid(row=2, column=0)

        Label(self.add_module_frame, text="Module name").grid(row=0, column=0, columnspan=2)
        name = Entry(self.add_module_frame)
        name.grid(row=1, column=1)
        Label(self.add_module_frame, text="Module code").grid(row=2, column=0, columnspan=2)
        code = Entry(self.add_module_frame)
        code.grid(row=3, column=1)
        add_module_button = Button(self.add_module_frame, text="Submit",
                                   command=lambda: [self.add_module_database(name.get(), code.get()),
                                                    self.add_module_frame.grid_forget()])
        add_module_button.grid(row=4, column=1, sticky='w', pady=20)
        quit_button = Button(self.add_module_frame, text="Quit", command=self.add_module_frame.grid_forget)
        quit_button.grid(row=4, column=1, sticky='e', pady=20)
        self.add_module_frame.grid(row=2, columnspan=4)

    def add_module_database(self, name, code):
        if name == "" or code == "":
            messagebox.showinfo("Invalid input", "Module name and code fields can not be empty.")
        else:
            if self.check_module_duplicate(code) == 1:
                messagebox.showinfo(message="Module code already exists in database")
            else:
                curr.execute('''INSERT INTO Modules(Name,Code) VALUES(?,?)''', (name, code,))
                conn.commit()
                self.update_module_tree()


class AnswerClass(Frame):
    """A frame class to display the answers for the selected module from the treeview, this class is inheriting from the tkinter object Frame."""

    def __init__(self, master):
        Frame.__init__(self, master)
        columns = ("column1", "column2", "column3")
        self.answer_treeview = TreeView(self, columns=columns)
        self.answer_treeview.tree.heading('#1', text='Answer')
        self.answer_treeview.tree.heading('#2', text='Is_Right')
        self.answer_treeview.tree.heading('#3', text="ID")
        self.answer_treeview.tree["displaycolumns"] = ("0", "1")
        self.update_answer_tree()
        self.answer_treeview.grid(row=0, column=0, sticky='nsew', columnspan=2)
        self.grid_columnconfigure([0, 1], weight=1)
        self.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self._back_button = Button(self, text="Back",
                                   command=self.question_switch_frame)
        self._back_button.grid(row=1, column=0, pady=20, sticky='ew')
        self.edit_button = Button(self, text="Edit", command=self.edit_answer)
        self.edit_button.grid(row=1, column=1, pady=20, sticky='ew')
        self.id_q = None
        self.edit_answer_frame = Frame(self)

    def edit_answer(self):
        """Function to implement and add the elements required for editing a module. The function automatically grabs
        the values of the selected child and inserts it into the entry boxes so that it's easier for the user to
        edit. After the user clicks submit, we check if there's a module."""
        try:

            lbl_1 = Label(self.edit_answer_frame, text="New Question Text")
            lbl_1.grid(row=0, column=1)
            name = Entry(self.edit_answer_frame)
            name.grid(row=1, column=1)
            lbl_2 = Label(self.edit_answer_frame, text="New Mark")
            lbl_2.grid(row=2, column=1)
            code = Entry(self.edit_answer_frame)
            code.grid(row=3, column=1)
            name.insert(0, self.answer_treeview.tree.item(self.answer_treeview.tree.focus())['values'][0])
            code.insert(0, self.answer_treeview.tree.item(self.answer_treeview.tree.focus())['values'][1])
            edit_module_button = Button(self.edit_answer_frame, text="Submit",
                                        command=lambda: [self.edit_answer_database(name.get(), code.get()),
                                                         self.edit_answer_frame.grid_forget()])
            edit_module_button.grid(row=4, column=1, pady=20, sticky='w')
            quit_button = Button(self.edit_answer_frame, text="Quit", command=self.edit_answer_frame.grid_forget)
            quit_button.grid(row=4, column=1, sticky='e', pady=20)
            self.edit_answer_frame.grid(row=2, columnspan=5)
            self.edit_answer_frame.tkraise()
        except Exception as e:
            logging.error(e)

    def edit_answer_database(self, name, code):

        """Function which is used to edit the Modules database using the name and code provided from the user. """

        try:
            id_q = (self.answer_treeview.tree.item(self.answer_treeview.tree.focus())['values'][2])

            if name == "" or code == "":
                messagebox.showinfo("Invalid input", "Question text and mark fields can not be empty.")
            else:
                message_edit = messagebox.askyesno("Confirmation", "Do you want to permanently update this question?",
                                                   parent=self.edit_answer_frame)
                if message_edit > 0:
                    curr.execute('''UPDATE Answers SET answer = ? , Is_Right = ? WHERE ID = ?''',
                                 (name, code, id_q))
                    conn.commit()
                    self.update_answer_tree()

        except Exception as e:
            print(e)

    def question_switch_frame(self):
        """"A function to switch the frame to the Question Class"""
        self.master.switch_frame(QuestionClass)

    def update_answer_tree(self):
        self.answer_treeview.tree.delete(*self.answer_treeview.tree.get_children())
        self.id_q = Receptor.id_q

        curr.execute('''SELECT Answer,Is_Right,ID FROM Answers WHERE Question_ID=(?)''', (self.id_q,))
        rows = curr.fetchall()
        for row in rows:
            self.answer_treeview.tree.insert("", END, values=row)


class ScrollableFrame(Frame):
    """A Tkinter scrollable frame. This frame only allows vertical scrolling"""

    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)

        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(_event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(_event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind('<Configure>', _configure_canvas)

        def _bound_to_mousewheel(_event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbound_to_mousewheel(_event):
            canvas.unbind_all("<MouseWheel>")

        def _on_mousewheel(_event):
            canvas.yview_scroll(int(-1 * (_event.delta / 120)), "units")

        interior.bind('<Enter>', _bound_to_mousewheel)
        interior.bind('<Leave>', _unbound_to_mousewheel)


def add_answer_db(question_id, answer_text, is_correct):
    if answer_text == "":
        messagebox.showerror(title="Error", message="Please ensure all the fields are filled")
    curr.execute('''INSERT INTO Answers(Question_ID, Answer, Is_Right) VALUES(?,?,?)''',
                 (question_id, answer_text, is_correct,))
    conn.commit()


class QuestionClass(Frame):
    """A frame class which contains everything related to the questions, the treeview containing the columns from the
    questions table in database and the buttons to add, edit, delete and search questions """

    def __init__(self, master):
        Frame.__init__(self, master)
        self.grid(row=0, column=0, sticky='news', padx=10, pady=10)
        columns = ("column1", "column2", "column3", "column4", "column5")
        self.tv = TreeView(self, columns=columns)
        self.tv.tree.heading('#1', text='Question')
        self.tv.tree.heading('#2', text='Type')
        self.tv.tree.heading('#3', text="Mark")
        self.tv.tree.heading('#4', text="ID")
        self.tv.tree.heading('#5', text="Module_ID")
        self.tv.tree["displaycolumns"] = ("0", "1", "2")
        self.update_question_treeview()
        self.tv.grid(row=0, column=0, columnspan=5, sticky='ew')
        self.grid_columnconfigure([0, 1, 2, 3, 4], weight=1)
        self.grid_rowconfigure([0, 1, 2], weight=1)
        self.tv.tree.bind("<Double-1>", self.module_switch_frame)
        self.back_button = Button(self, text="Back", command=self.back_function)
        self.back_button.grid(row=1, column=0, pady=20, sticky='ew')
        self.add_question_button = Button(self, text="Add question",
                                          command=self.add_question)
        self.add_question_button.grid(row=1, column=1, pady=20, sticky='ew')
        self.search_question_frame = Frame(self)
        self.search_button = Button(self, text="search", command=self.search_view)
        self.search_button.grid(row=1, column=4, pady=20, sticky='ew')

        self.edit_question_button = Button(self, text="Edit question",
                                           command=lambda: [self.forget_bottom_frames(), self.check_edit_focus(),
                                                            self.edit_question()])
        self.edit_question_button.grid(row=1, column=2, pady=20, sticky='ew')
        self.delete_question_button = Button(self, text="Delete question", command=lambda: [self.delete_question()])
        self.delete_question_button.grid(row=1, column=3, pady=20, sticky='ew')
        self.edit_question_frame = Frame(self)

        self.add_question_frame = Frame(self)

        self.frame = ScrollableFrame(self)
        self.single_correct_frame = ScrollableFrame(self)
        self.multiple_correct_frame = ScrollableFrame(self)
        self.true_false_frame = ScrollableFrame(self)
        self.id_m = None
        self.id_q = None
        self.question_text = StringVar()

    def add_question_db(self, question_text, mark, question_type, module_id):
        """A function to add questions to the database."""
        if question_text == "" or mark == "":
            messagebox.showerror(title="Error", message="Please ensure all the fields are filled")
        else:
            if self.check_question_duplicate(question_text) == 1:
                curr.execute('''UPDATE Questions SET Question = ? , Mark = ? , Type = ? WHERE Question = ?''',
                             (question_text, mark, question_type, question_text,))
                messagebox.showinfo(message="Question already exists in database")
            else:
                curr.execute('''INSERT INTO Questions(Question,Mark,Type,Module_ID) VALUES(?,?,?,?)''',
                             (question_text, mark, question_type, module_id,))
                conn.commit()

    def check_edit_focus(self):

        """A function to check if a TreeView item is selected or not. If it is not selected we would display a
        messagebox error to let the user know that it is not selected and if it selected we will continue to execute
        the function we require to run. """

        if self.tv.tree.focus() != "":

            self.edit_question()
        else:
            messagebox.showinfo(message="Please select a question")

    def back_function(self):
        """A function to switch the frame to the main module frame once the back butto is clicked"""
        self.master.switch_frame(ModuleClass)

    def module_switch_frame(self, _event):
        """A function to switch frame to answer class"""
        self.id_q = (self.tv.tree.item(self.tv.tree.focus())['values'][3])
        Receptor.id_q = self.id_q
        self.master.switch_frame(AnswerClass)

    def forget_bottom_frames(self):
        """A function to forget the bottom frames to make space for other frames to appear"""
        self.add_question_frame.grid_forget()
        self.edit_question_frame.grid_forget()
        self.search_question_frame.grid_forget()
        self.single_correct_frame.grid_forget()
        self.multiple_correct_frame.grid_forget()
        self.true_false_frame.grid_forget()

    def search_view(self):
        """A function to display the search option"""
        self.forget_bottom_frames()
        self.search_question_frame.grid_columnconfigure((0, 2), weight=1)
        self.search_question_frame.grid_rowconfigure([0, 1], weight=1)
        self.search_question_frame.grid(row=2, column=1, columnspan=3)
        search_entry_label = Label(self.search_question_frame, text="Search")
        search_entry_label.grid(row=0, column=1, sticky='ew')
        search_entry = Entry(self.search_question_frame)
        search_entry.grid(row=1, column=1, sticky='ew')
        search_button_iframe = Button(self.search_question_frame, text="Search",
                                      command=lambda: [self.tv.search(search_entry.get())])
        search_button_iframe.grid(row=2, column=1, pady=20, sticky='w')
        search_quit_button = Button(self.search_question_frame, text="Quit",
                                    command=self.search_question_frame.grid_forget)
        search_quit_button.grid(row=2, column=1, sticky='e', pady=20)

    def update_question_treeview(self):
        """A function to update the question TreeView based on the selected module"""
        self.tv.tree.delete(*self.tv.tree.get_children())
        self.id_m = Receptor.id_m

        curr.execute('''SELECT Question,Type,Mark,ID,Module_ID FROM Questions WHERE MODULE_ID=(?)''', (self.id_m,))
        rows = curr.fetchall()
        for row in rows:
            self.tv.tree.insert("", END, values=row)

    def edit_question(self):

        """Function to implement and add the elements required for editing a question. The function automatically grabs
        the values of the selected child and inserts it into the entry boxes so that it's easier for the user to
        edit."""
        try:

            lbl_1 = Label(self.edit_question_frame, text="New Question Text")
            lbl_1.grid(row=0, column=1)
            name = Entry(self.edit_question_frame)
            name.grid(row=1, column=1)
            lbl_2 = Label(self.edit_question_frame, text="New Mark")
            lbl_2.grid(row=2, column=1)
            code = Entry(self.edit_question_frame)
            code.grid(row=3, column=1)
            name.insert(0, self.tv.tree.item(self.tv.tree.focus())['values'][0])
            code.insert(0, self.tv.tree.item(self.tv.tree.focus())['values'][2])
            edit_module_button = Button(self.edit_question_frame, text="Submit",
                                        command=lambda: [self.edit_question_database(name.get(), code.get()),
                                                         self.edit_question_frame.grid_forget()])
            edit_module_button.grid(row=4, column=1, pady=20, sticky='w')
            quit_button = Button(self.edit_question_frame, text="Quit", command=self.edit_question_frame.grid_forget)
            quit_button.grid(row=4, column=1, sticky='e', pady=20)
            self.edit_question_frame.grid(row=2, columnspan=5)
            self.edit_question_frame.tkraise()
        except Exception as e:
            logging.error(e)

    def edit_question_database(self, name, code):

        """Function which is used to edit the questions database using the name and code provided from the user. """

        try:
            id_q = (self.tv.tree.item(self.tv.tree.focus())['values'][3])

            if name == "" or code == "":
                messagebox.showinfo("Invalid input", "Question text and mark fields can not be empty.")
            else:
                message_edit = messagebox.askyesno("Confirmation", "Do you want to permanently update this question?",
                                                   parent=self.edit_question_frame)
                if message_edit > 0:
                    curr.execute('''UPDATE Questions SET question = ? , mark = ? WHERE ID = ?''',
                                 (name, code, id_q))
                    conn.commit()
                    self.update_question_treeview(),

        except Exception as e:
            print(e)

    def delete_question(self):
        """A function to delete a selected question from the treeview and the database"""
        try:
            id_q = (self.tv.tree.item(self.tv.tree.focus())['values'][3])

            message_delete = messagebox.askyesno("Confirmation", "Do you want to permanently delete this module?")
            if message_delete > 0:
                self.forget_bottom_frames()
                curr.execute('''DELETE FROM Questions WHERE ID=(?)''', (id_q,))
                curr.execute('''DELETE FROM Answers WHERE Question_ID=(?)''', (id_q,))
                conn.commit()
                conn.commit()
                self.update_question_treeview()

        except Exception as e:
            print(e)

    @staticmethod
    def check_question_duplicate(question):
        """A function to check for duplicate questions in the database"""

        response = conn.execute("SELECT EXISTS(SELECT 1 FROM Questions WHERE Question=?)", (question,))
        fetched = response.fetchone()[0]
        return fetched

    def add_question(self):
        """A function to configure the frame placement for add question. It has three buttons based on the three question types(Single correct, Multiple correct and True/False)"""
        self.forget_bottom_frames()
        Label(self.add_question_frame, text="Which type of question would you like to add?").grid(row=0, column=0,
                                                                                                  pady=10)
        multiple_choice_button = Button(self.add_question_frame, text="Multiple correct choice",
                                        command=lambda: [self.forget_bottom_frames(),
                                                         self.add_multiple_choice_question()])
        multiple_choice_button.grid(row=1, column=0, pady=10)

        single_choice_button = Button(self.add_question_frame, text="Single correct choice",
                                      command=lambda: [self.forget_bottom_frames(), self.add_single_choice_question()])
        single_choice_button.grid(row=2, column=0, pady=10)

        true_false_button = Button(self.add_question_frame, text="True False",
                                   command=lambda: [self.forget_bottom_frames(), self.add_true_false_question()])
        true_false_button.grid(row=3, column=0, pady=10)
        self.add_question_frame.grid(row=2, columnspan=5)
        self.add_question_frame.tkraise()

    def add_multiple_choice_question(self):
        """A function which configures the frame grid placement for adding multiple correct option questions"""
        """The sqlite3 statement below would basically help us prevent having gaps in our autoincrement IDs"""
        curr.execute('''UPDATE sqlite_sequence SET seq = (SELECT MAX(ID) FROM questions) WHERE name="questions"''')
        self.multiple_correct_frame.grid(row=3, column=0, sticky='NSEW', columnspan=5)
        self.multiple_correct_frame.interior.grid_columnconfigure([0, 1, 2, 3, 4], weight=1)
        Label(self.multiple_correct_frame.interior, text="Question Text").grid(row=0, column=0, columnspan=5, pady=10)
        multiple_question_text = Entry(self.multiple_correct_frame.interior, textvariable=self.question_text, width=50)
        multiple_question_text.grid(row=1, column=0, columnspan=5, pady=10)
        Label(self.multiple_correct_frame.interior, text="Correct Options").grid(row=0, column=2, columnspan=5, pady=10)

        Label(self.multiple_correct_frame.interior, text="Option 1").grid(row=2, column=0, columnspan=5, pady=10)
        self.multiple_option_1 = Entry(self.multiple_correct_frame.interior, width=50)
        self.multiple_option_1.grid(row=3, column=0, columnspan=5, pady=10)
        self.multiple_checkbutton_var_1 = BooleanVar()
        checkbutton_1 = Checkbutton(self.multiple_correct_frame.interior, variable=self.multiple_checkbutton_var_1,
                                    onvalue=True,
                                    offvalue=False)
        checkbutton_1.grid(row=2, column=2, columnspan=5, pady=10)

        Label(self.multiple_correct_frame.interior, text="Option 2").grid(row=5, column=0, columnspan=5, pady=10)
        self.multiple_option_2 = Entry(self.multiple_correct_frame.interior, width=50)
        self.multiple_option_2.grid(row=6, column=0, columnspan=5, pady=10)
        self.multiple_checkbutton_var_2 = BooleanVar()
        checkbutton_2 = Checkbutton(self.multiple_correct_frame.interior, variable=self.multiple_checkbutton_var_2,
                                    onvalue=True,
                                    offvalue=False)
        checkbutton_2.grid(row=5, column=2, columnspan=5, pady=10)

        Label(self.multiple_correct_frame.interior, text="Option 3").grid(row=8, column=0, columnspan=5, pady=10)
        self.multiple_option_3 = Entry(self.multiple_correct_frame.interior, width=50)
        self.multiple_option_3.grid(row=9, column=0, columnspan=5, pady=10)
        self.multiple_checkbutton_var_3 = BooleanVar()
        checkbutton_3 = Checkbutton(self.multiple_correct_frame.interior, variable=self.multiple_checkbutton_var_3,
                                    onvalue=True,
                                    offvalue=False)
        checkbutton_3.grid(row=8, column=2, columnspan=5, pady=10)

        Label(self.multiple_correct_frame.interior, text="Option 4").grid(row=11, column=0, columnspan=5, pady=10)
        self.multiple_option_4 = Entry(self.multiple_correct_frame.interior, width=50)
        self.multiple_option_4.grid(row=12, column=0, columnspan=5, pady=10)
        self.multiple_checkbutton_var_4 = BooleanVar()
        checkbutton_4 = Checkbutton(self.multiple_correct_frame.interior, variable=self.multiple_checkbutton_var_4,
                                    onvalue=True,
                                    offvalue=False)
        checkbutton_4.grid(row=11, column=2, columnspan=5, pady=10)
        self.multiple_description = Entry(self.multiple_correct_frame.interior, width=50)
        self.multiple_description.grid(row=13, column=0, columnspan=5, pady=10)

        Label(self.multiple_correct_frame.interior, text="Mark if all correct").grid(row=14, column=0, columnspan=5,
                                                                                     pady=10)
        mark = Entry(self.multiple_correct_frame.interior, width=50)
        mark.grid(row=15, column=0, columnspan=5, pady=10)
        question_type = "Multiple choice"

        def add_ans():
            """A function to get the information out of the add question frame"""
            add_all_answers(self.multiple_option_1.get(), self.multiple_checkbutton_var_1.get(),
                            self.multiple_description.get())
            add_all_answers(self.multiple_option_2.get(), self.multiple_checkbutton_var_2.get(),
                            self.multiple_description.get())
            add_all_answers(self.multiple_option_3.get(), self.multiple_checkbutton_var_3.get(),
                            self.multiple_description.get())
            add_all_answers(self.multiple_option_4.get(), self.multiple_checkbutton_var_4.get(),
                            self.multiple_description.get())

        def add_all_answers(answer, is_correct, description):
            """A function which takes in the information entered to add questions and then adds all of that to the database"""
            curr.execute('SELECT max(id) FROM Questions')
            max_id = curr.fetchone()[0]

            curr.execute(
                '''INSERT INTO Answers(Question_ID, Answer, Is_Right, Description) VALUES(?,?,?,?)''',
                (int(max_id), answer, is_correct, description,))

            conn.commit()

        submit_button = Button(self.multiple_correct_frame.interior, text='Submit', command=lambda: [
            self.add_question_db(multiple_question_text.get(), mark.get(), question_type, module_id=Receptor.id_m, ),
            add_ans(),
            self.update_question_treeview()])
        submit_button.grid(row=16, column=0, columnspan=5, pady=10)
        quit_button = Button(self.multiple_correct_frame.interior, text='Quit',
                             command=self.multiple_correct_frame.grid_forget)
        quit_button.grid(row=17, column=0, columnspan=5, pady=5)

    def add_single_choice_question(self):
        """A function to configure the frame placement and objects in the frame to add single correct questions"""
        curr.execute('''UPDATE sqlite_sequence SET seq = (SELECT MAX(ID) FROM questions) WHERE name="questions"''')
        self.single_correct_frame.grid(row=3, column=0, sticky='NSEW', columnspan=5)
        self.single_correct_frame.interior.grid_columnconfigure([0, 1, 2, 3, 4], weight=1)
        Label(self.single_correct_frame.interior, text="Question Text").grid(row=0, column=0, columnspan=5, pady=10)
        question_text = Entry(self.single_correct_frame.interior, width=50, textvariable=self.question_text)
        question_text.grid(row=1, column=0, columnspan=5, pady=10)
        Label(self.single_correct_frame.interior, text="Correct Options").grid(row=0, column=2, columnspan=5, pady=10)

        Label(self.single_correct_frame.interior, text="Option 1").grid(row=2, column=0, columnspan=5, pady=10)
        option_1 = Entry(self.single_correct_frame.interior, width=50)
        option_1.grid(row=3, column=0, columnspan=5, pady=10)
        radio_button_var = IntVar()
        radio_button_1 = Radiobutton(self.single_correct_frame.interior, variable=radio_button_var, value=1)
        radio_button_1.grid(row=2, column=2, columnspan=5, pady=10)

        Label(self.single_correct_frame.interior, text="Option 2").grid(row=5, column=0, columnspan=5, pady=10)
        option_2 = Entry(self.single_correct_frame.interior, width=50)
        option_2.grid(row=6, column=0, columnspan=5, pady=10)
        radio_button_2 = Radiobutton(self.single_correct_frame.interior, variable=radio_button_var, value=2)
        radio_button_2.grid(row=5, column=2, columnspan=5, pady=10)

        Label(self.single_correct_frame.interior, text="Option 3").grid(row=8, column=0, columnspan=5, pady=10)
        option_3 = Entry(self.single_correct_frame.interior, width=50)
        option_3.grid(row=9, column=0, columnspan=5, pady=10)
        radio_button_3 = Radiobutton(self.single_correct_frame.interior, variable=radio_button_var, value=3)
        radio_button_3.grid(row=8, column=2, columnspan=5, pady=10)
        Label(self.single_correct_frame.interior, text="Option 4").grid(row=11, column=0, columnspan=5, pady=10)
        option_4 = Entry(self.single_correct_frame.interior, width=50)
        option_4.grid(row=12, column=0, columnspan=5, pady=10)
        radio_button_4 = Radiobutton(self.single_correct_frame.interior, variable=radio_button_var, value=4)
        radio_button_4.grid(row=11, column=2, columnspan=5, pady=10)
        description_4 = Entry(self.single_correct_frame.interior, width=50)
        description_4.grid(row=13, column=0, columnspan=5, pady=10)

        Label(self.single_correct_frame.interior, text="Mark if all correct").grid(row=14, column=0, columnspan=5,
                                                                                   pady=10)
        mark = Entry(self.single_correct_frame.interior, width=50)
        mark.grid(row=15, column=0, columnspan=5, pady=10)
        question_type = "Single choice"

        def is_correct(n):
            """A function to get the chosen radio button option"""
            if radio_button_var.get() == n:
                return 1
            else:
                return 0

        def add_ans():
            """A function to get all the information from the add single correct choice question frame"""
            add_all_answers(option_1.get(), is_correct(1), description_4.get())
            add_all_answers(option_2.get(), is_correct(2), description_4.get())
            add_all_answers(option_3.get(), is_correct(3), description_4.get())
            add_all_answers(option_4.get(), is_correct(4), description_4.get())

        def add_all_answers(answer, is_right_option, description):
            """A function to add all the information entered in the add question frame to the database"""
            curr.execute('SELECT max(id) FROM Questions')
            max_id = curr.fetchone()[0]

            curr.execute(
                '''INSERT INTO Answers(Question_ID, Answer, Is_Right, description) VALUES(?,?,?,?)''',
                (max_id, answer, int(is_right_option), description))
            conn.commit()
        submit_button = Button(self.single_correct_frame.interior, text='Submit', command=lambda: [
            self.add_question_db(question_text.get(), mark.get(), question_type, module_id=Receptor.id_m, ), add_ans(),
            self.update_question_treeview()])
        submit_button.grid(row=16, column=0, columnspan=5, pady=10)
        quit_button = Button(self.single_correct_frame.interior, text='Quit',
                             command=self.single_correct_frame.grid_forget)
        quit_button.grid(row=17, column=0, columnspan=5, pady=5)

    def add_true_false_question(self):
        """A function to configure the objects inside the frame to add true false questions"""
        curr.execute('''UPDATE sqlite_sequence SET seq = (SELECT MAX(ID) FROM questions) WHERE name="questions"''')
        self.true_false_frame.grid(row=3, column=0, sticky='NEWS', columnspan=5)
        self.true_false_frame.interior.grid_columnconfigure([0, 1, 2, 3, 4], weight=1)
        Label(self.true_false_frame.interior, text="Question Text").grid(row=0, column=0, columnspan=5, pady=5)
        question_text = Entry(self.true_false_frame.interior, width=50)
        question_text.grid(row=1, column=0, columnspan=5, pady=5)
        Label(self.true_false_frame.interior, text="True/False").grid(row=2, column=0, columnspan=5, pady=5)
        clicked = StringVar()
        clicked.set("Choose one")
        options = ["True", "False"]
        true_false_menu = OptionMenu(self.true_false_frame.interior, clicked, *options)
        true_false_menu.grid(row=3, column=0, columnspan=5, pady=5)

        Label(self.true_false_frame.interior, text="Mark if all correct").grid(row=4, column=0, columnspan=5, pady=5)
        mark = Entry(self.true_false_frame.interior, width=50)
        mark.grid(row=5, column=0, columnspan=5, pady=5)
        question_type = "True/False"

        def add_all_answers(answer):
            """A function to add all the information entered in the add true false question frame to the database"""
            curr.execute('SELECT max(id) FROM Questions')
            max_id = curr.fetchone()[0]

            if answer == "True":
                curr.execute('''INSERT INTO Answers(Question_ID, Answer, Is_Right) VALUES(?,?,?)''',
                             (max_id, answer, 1,))
                curr.execute('''INSERT INTO Answers(Question_ID, Answer, Is_Right) VALUES(?,?,?)''',
                             (max_id, "False", 0,))
            elif answer == "False":
                curr.execute('''INSERT INTO Answers(Question_ID, Answer, Is_Right) VALUES(?,?,?)''',
                             (max_id, "True", 0,))
                curr.execute('''INSERT INTO Answers(Question_ID, Answer, Is_Right) VALUES(?,?,?)''',
                             (max_id, answer, 1,))
            conn.commit()

        submit_button = Button(self.true_false_frame.interior, text='Submit', command=lambda: [
            self.add_question_db(question_text.get(), mark.get(), question_type, module_id=Receptor.id_m, ),
            add_all_answers(clicked.get()),
            self.update_question_treeview()])
        submit_button.grid(row=16, column=0, columnspan=5, pady=10)
        quit_button = Button(self.true_false_frame.interior, text='Quit', command=self.true_false_frame.grid_forget)
        quit_button.grid(row=17, column=0, columnspan=5, pady=5)


def set_geometry(screen, window_height, window_width):
    """A function to set the geometry of the main window"""
    x_coordinate = int((screen.winfo_screenwidth() / 2) - (window_width / 2))
    y_coordinate = int((screen.winfo_screenheight() / 2) - (window_height / 2))
    screen.geometry("{}x{}+{}+{}".format(window_width, window_height, x_coordinate, y_coordinate))


# main window function
class Launch:
    """A simple class to launch the administrative features and the splash screen"""
    def __init__(self):
        self.splash_root = None

    def splash(self):
        self.splash_root = Tk()
        set_geometry(self.splash_root, 300, 400)
        img = PhotoImage(master=self.splash_root, file='res/quiz.png')
        Label(self.splash_root, image=img).pack()
        self.splash_root.after(1000, self.main)
        mainloop()

    def main(self):
        # destroy splash window
        self.splash_root.destroy()
        # Execute tkinter
        app = MainFrame()
        set_geometry(app, app.winfo_screenheight(), app.winfo_screenwidth())
        app.title("Quiztion")
        app.grid_rowconfigure(1, weight=1)
        app.grid_columnconfigure(0, weight=1)


launch = Launch()
if __name__ == "__main__":
    launch.splash()
