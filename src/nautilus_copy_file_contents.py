import mimetypes
import os
import subprocess
import sys
from urllib.parse import unquote

import gi
gi.require_version('Nautilus', '4.0')
from gi.repository import Nautilus, GObject, Gtk, Gdk, Gio, GdkPixbuf

# mimetypes.guess_type with file path is deprecated for python>=3.13
if sys.version_info.major == 3 and sys.version_info.minor < 13:
    mimetypes.guess_file_type = mimetypes.guess_type

# Use magic if available to get MIME type from file content
try:
    import magic
    magic_mime = magic.open(magic.MAGIC_MIME_TYPE | magic.MAGIC_SYMLINK)
    magic_mime.load()
except ModuleNotFoundError:
    magic_mime = None


def get_mime_type(file_path):
    """Return the MIME type of the specified file."""
    if magic_mime is None:
        return mimetypes.guess_file_type(file_path)[0] or 'unknown'
    return magic_mime.file(file_path)


class CopyFileContents(GObject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        super().__init__()
        self.image_mime_types = set()
        for f in GdkPixbuf.Pixbuf.get_formats():
            self.image_mime_types.update(f.get_mime_types())


    def is_supported_mime_type(self, mime_type):
        white_list = ["application/json", "application/xml", "application/x-shellscript", "application/x-tiled-tsx", "application/vnd.dart", "application/toml", "application/x-gtk-builder"]
        return mime_type.startswith("text/") or mime_type in white_list

    def send_notification(self, title, message):
        """Send a notification with the specified title and message."""
        notification = Gio.Notification.new(title)
        notification.set_body(message)
        Gio.Application.get_default().send_notification(None, notification)

    def copy_to_clipboard(self, content):
        """Copy the specified content to the clipboard."""
        clipboard = Gdk.Display.get_default().get_clipboard() 
        if isinstance(content, Gdk.ContentProvider):
            clipboard.set_content(content)
        else:
            clipboard.set(content)  # Set the text to the clipboard

    def get_file_items(self, files):
        """Return menu items for supported file types."""
        if len(files) == 1:
            file_info = files[0]
            file_path = unquote(file_info.get_uri()[7:])
            mime_type = get_mime_type(file_path)  # Get MIME type
            if self.is_supported_mime_type(mime_type) or mime_type in self.image_mime_types:
                menu_item = Nautilus.MenuItem(
                    name='CopyFileContents::Read_File',
                    label='Copy File Content',
                    tip='Reads the content of the selected file',
                )
                menu_item.connect('activate', self.copy_file_content, file_path, mime_type)
                return [menu_item]
        return []

    def copy_file_content(self, menu, file_path, mime_type):
        """Read the content of the selected file and copy it to the clipboard."""
        if os.path.isfile(file_path):
            file_name = os.path.basename(file_path)
            try:
                if mime_type in self.image_mime_types:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file(file_path)
                    texture = Gdk.Texture.new_for_pixbuf(pixbuf)
                    png_bytes = texture.save_to_png_bytes()
                    content = Gdk.ContentProvider.new_for_bytes('image/png', png_bytes)
                else:
                    with open(file_path, 'r') as f:
                        content = f.read()
                self.copy_to_clipboard(content)  # Copy content to clipboard
                self.send_notification("Content Copied", f"The content of the file '{file_name}' has been copied successfully.")
            except Exception as e:
                self.send_notification(f"Cannot read the contents of '{file_name}'", str(e))
                print(f"Error reading file '{file_name}': {e}")
        else:
            print(f"{file_path} is not a valid file.")
