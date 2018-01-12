from django.forms.fields import ChoiceField
import re
import os


class RelativeFilePathFieldForm(ChoiceField):
    """
    Custom form for RelativeFilePathField. Most of code from django.forms.FilePathField
    """
    def __init__(self, path, match=None, recursive=False, allow_files=True,
                 allow_folders=False, rel_path='', **kwargs):
        self.path, self.match, self.recursive, self.rel_path = path, match, recursive, rel_path
        self.allow_files, self.allow_folders = allow_files, allow_folders
        super(RelativeFilePathFieldForm, self).__init__(choices=(),  **kwargs)

        if self.required:
            self.choices = []
        else:
            self.choices = [("", "---------")]

        if self.match is not None:
            self.match_re = re.compile(self.match)

        if recursive:
            for root, dirs, files in sorted(os.walk(self.path)):
                if self.allow_files:
                    for f in files:
                        if self.match is None or self.match_re.search(f):
                            f = os.path.join(root, f)
                            name = f.replace(path, "", 1)
                            name = name[1:] if name.startswith('/') else name
                            rel_path = os.path.join(self.rel_path, name)
                            self.choices.append((rel_path, name))
                if self.allow_folders:
                    for f in dirs:
                        if f == '__pycache__':
                            continue
                        if self.match is None or self.match_re.search(f):
                            f = os.path.join(root, f)
                            name = f.replace(path, "", 1)
                            name = name[1:] if name.startswith('/') else name
                            rel_path = os.path.join(self.rel_path, name)
                            self.choices.append((rel_path, name))
        else:
            try:
                for f in sorted(os.listdir(self.path)):
                    if f == '__pycache__':
                        continue
                    full_file = os.path.join(self.path, f)
                    rel_file = os.path.join(self.rel_path, f)
                    if (((self.allow_files and os.path.isfile(full_file)) or
                        (self.allow_folders and os.path.isdir(full_file))) and
                        (self.match is None or self.match_re.search(f))):
                        self.choices.append((rel_file, f))
            except OSError:
                pass

        self.widget.choices = self.choices