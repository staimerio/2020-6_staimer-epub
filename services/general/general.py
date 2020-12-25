# Os
import os

# Re
import re

# Unicodedata
import unicodedata

def rmfile(path):
    """Delete files from a path

    :param path: Path of the folder with files to will delete
    """
    os.remove(path)

def slugify(text: str = ""):
    """Simplifies ugly strings into something URL-friendly.

    :param text: Text to simplifies in ``str`` type    
    """
    # Reference: https://github.com/mikaelho/docgen/blob/master/docgen.py
    # "[Some] _ Article's Title--"
    # "[some] _ article's title--"
    text = str(text).lower()
    # "[some] _ article's_title--"
    # "[some]___article's_title__"
    for c in [' ', '-', '.', '/']:
        text = text.replace(c, '_')
    # "[some]___article's_title__"
    # "some___articles_title__"
    text = re.sub('\W', '', text)
    # "some___articles_title__"
    # "some   articles title  "
    text = text.replace('_', ' ')

    # "some   articles title  "
    # "some articles title "
    text = re.sub('\s+', ' ', text)

    # "some articles title "
    # "some articles title"
    text = text.strip()

    # "some articles title"
    # "some-articles-title"
    text = text.replace(' ', '-')
    # delete acents
    text = unicodedata.normalize("NFD", text)
    # text = text.encode("utf8").decode("ascii", "ignore")
    # text = urlencode(text)
    return text