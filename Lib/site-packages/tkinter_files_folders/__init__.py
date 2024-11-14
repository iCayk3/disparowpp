import os
from tkinter import filedialog


def get_multiple_files_with_tkinter(filetypes=((".txt", "*.txt"),)):
    files = filedialog.askopenfilename(filetypes=filetypes, multiple=True)
    files = [os.path.normpath(x) for x in files]
    return files


def get_file_with_tkinter(filetypes=((".txt", "*.txt"),)):
    file = filedialog.askopenfilename(filetypes=filetypes, multiple=False)
    return os.path.normpath(file)


def get_save_file_with_tkinter(filetypes=((".txt", "*.txt"),)):
    file = filedialog.asksaveasfilename(filetypes=filetypes)
    return os.path.normpath(file)


def get_existing_directory_with_tkinter():
    file = filedialog.askdirectory(mustexist=True)
    return os.path.normpath(file)


def get_not_existing_directory_with_tkinter():
    file = filedialog.askdirectory(mustexist=False)
    return os.path.normpath(file)

