# Nautilus Extension: Copy File Contents

Easily copy the contents of a text file! 😄  
![Screenshot showing the option in the right-click menu](https://github.com/user-attachments/assets/7fb749a3-25ee-4eae-b644-00c07510c11d)

## Why?

I often needed to copy the content of a file, and using the "preview" with
<kbd>SPACE</kbd> to copy it wasn’t the best for me. So, I decided to create
this small project to streamline the process and also learn more about
developing Nautilus extensions! 🚀

## Dependencies

You'll need to install [nautilus-python](https://gitlab.gnome.org/GNOME/nautilus-python) for your distribution. 🙂

Optionally, for more advanced file type detection you may install [python-magic](https://github.com/ahupp/python-magic).

## Installation

```bash
make install
```

or manually:

```bash
cp ./src/nautilus_copy_file_contents.py $HOME/.local/share/nautilus-python/extensions/
```

## Uninstallation

```bash
make uninstall
```

or manually:

```bash
rm $HOME/.local/share/nautilus-python/extensions/nautilus_copy_file_contents.py
```

## Development/Debugging

To install the latest version, close all Nautilus instances and reopen it! 😄

```bash
export NAUTILUS_PYTHON_DEBUG=misc
make install && nautilus -q
nautilus
```

Contributions are welcome! :heart:
