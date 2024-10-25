import gi
import subprocess
gi.require_version('Nautilus', '4.0')
from gi.repository import Nautilus, GObject, Gtk, Gdk, Gio, GdkPixbuf
import os
from urllib.parse import unquote


class CopyFileContents(GObject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        super().__init__()
        self.image_mime_types = set()
        for f in GdkPixbuf.Pixbuf.get_formats():
            self.image_mime_types.update(f.get_mime_types())


    def is_supported_mime_type(self, mime_type):
        white_list = ["application/json", "application/xml", "application/x-shellscript", "application/x-tiled-tsx", "application/vnd.dart", "application/toml", "application/x-gtk-builder"]
        return mime_type.startswith("text/") or mime_type in white_list

    def get_mime_type(self, file_path):
        """Return the MIME type of the specified file."""
        file = Gio.File.new_for_path(file_path)
        try:
            info = file.query_info('*', Gio.FileQueryInfoFlags.NONE, None)
            return info.get_content_type()
        except Exception as e:
            print(f"Error retrieving MIME type for '{file_path}': {e}")
            return None

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
        menu_items = []
        mime_types = []

        for file_info in files:
            file_path = unquote(file_info.get_uri()[7:])
            mime_type = self.get_mime_type(file_path)  # Get MIME type
            mime_types.append(mime_type)

            if self.is_supported_mime_type(mime_type) or mime_type in self.image_mime_types:
                menu_item = Nautilus.MenuItem(
                    name='CopyFileContents::Read_File',
                    label='Copy File Content',
                    tip='Reads the content of the selected file',
                )
                menu_item.connect('activate', self.copy_file_content, files, mime_types)
                menu_items.append(menu_item)

        return menu_items

    def copy_file_content(self, menu, files, mime_types):
        """Read the content of the selected files and copy it to the clipboard."""
        for file_info, mime_type in zip(files, mime_types):
            file_path = unquote(file_info.get_uri()[7:])
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
