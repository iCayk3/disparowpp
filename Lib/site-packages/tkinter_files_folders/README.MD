# Some tkinter functions for selecting files/folders 

```python
# Tested with:
# Python 3.9.13
# Windows 10

pip install tkinter-files-folders

from tkinter_files_folders import (
    get_multiple_files_with_tkinter,
    get_file_with_tkinter,
    get_save_file_with_tkinter,
    get_existing_directory_with_tkinter,
    get_not_existing_directory_with_tkinter,
)
get_multiple_files_with_tkinter(filetypes=((".txt", "*.txt"), (".png", "*.png")))
get_file_with_tkinter(filetypes=((".txt", "*.txt"), (".png", "*.png")))
get_save_file_with_tkinter(filetypes=((".txt", "*.txt"), (".png", "*.png")))
get_existing_directory_with_tkinter()
get_not_existing_directory_with_tkinter()

```



