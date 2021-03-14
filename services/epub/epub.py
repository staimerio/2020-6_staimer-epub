"""Servicios para el controlador de archivos"""

# Retic
from retic import env, App as app

# Ebooklib
from ebooklib import epub

# Os
import os

# Binascii
import binascii

# PIL
from PIL import Image

# Asyncio
import asyncio

# Aiohttp
import aiohttp

# Services
from retic.services.responses import success_response_service, error_response_service

# Utils
from services.general.general import rmfile, slugify

# Requets
import requests

# Constants
EPUB_BOOK_LANG = app.config.get('EPUB_BOOK_LANG')
EPUB_BOOK_AUTHOR = app.config.get('EPUB_BOOK_AUTHOR')
EPUB_OUT_PATH = app.config.get('EPUB_OUT_PATH')
EPUB_CSS_STYLE = '''@namespace epub "http://www.idpf.org/2007/ops";body{font-family:Cambria,Liberation Serif,Bitstream Vera Serif,Georgia,Times,Times New Roman,serif}h2{text-align:left;text-transform:uppercase;font-weight:200}ol{list-style-type:none}ol>li:first-child{margin-top:.3em}nav[epub|type~=toc]>ol>li>ol{list-style-type:square}nav[epub|type~=toc]>ol>li>ol>li{margin-top:.3em}'''


def build_from_html(title, cover, sections, binary_response=False, resources=[]):
    """Build a epub file from html content with a section list

    :param title: Title of the book
    :param cover: Cover in HTML
    :param sections: Sections of the book, it has a list of chapters
    :param binary_response: Flag that assign if the response will has a binary file
    """

    """Create a book instance"""
    _book = epub.EpubBook()
    """Set all metadata to book"""
    _book.set_title(title.upper())
    _book.set_language(EPUB_BOOK_LANG)
    _book.add_author(EPUB_BOOK_AUTHOR)
    """Create table of chapters"""
    _book.toc = ()
    """Create spine"""
    _book.spine = ['nav']
    """Add cover if it exists"""
    if cover:
        _ch_toc = ()
        _c1 = epub.EpubHtml(
            title="Cover",
            file_name="cover.xhtml",
            lang=EPUB_BOOK_LANG
        )
        _c1.content = cover
        """Add cover to book"""
        _book.add_item(_c1)
        """Add cover to spine"""
        _book.spine.append(_c1)
        _ch_toc += (_c1,)
        _book.toc += (
            (epub.Section("About it"), _ch_toc),
        )
    """For each section do the following"""
    for _idx_sec, _section in enumerate(sections):
        _ch_toc = ()
        """For each chapter do the following"""
        for _idx_ch, _chapter in enumerate(_section['chapters']):
            """Set valid chapter format"""
            _file_name = "{0}_{1}.xhtml".format(_idx_sec, _idx_ch)
            _c1 = epub.EpubHtml(
                title=_chapter['title'].capitalize(),
                file_name=_file_name,
                lang=EPUB_BOOK_LANG
            )
            _c1.content = _chapter['content']
            """Add chapter to book"""
            _book.add_item(_c1)
            """Add chapter to spine"""
            _book.spine.append(_c1)
            _ch_toc += (_c1,)
        """Create table of contents"""
        _book.toc += (
            (epub.Section("Chapters"), _ch_toc),
        )
    """Add navigation items"""
    _book.add_item(epub.EpubNcx())
    _book.add_item(epub.EpubNav())
    """Set css style"""
    _nav_css = epub.EpubItem(
        uid="style_nav", file_name="style/nav.css",
        media_type="text/css", content=EPUB_CSS_STYLE
    )
    """Add css style to epub"""
    _book.add_item(_nav_css)
    """Define out filename"""
    _out_fname = "{0}/{1}.epub".format(
        EPUB_OUT_PATH,
        _book.uid
    )

    # async def add_resource(_resource):
    #     """Add resources"""
    #     if _resource['type'] == 'image_url':
    #         _image_item = await get_resource_image_item(
    #             _resource['url'],
    #             _resource['file_name'],
    #             _resource.get('headers')
    #         )
    #         # add Image file
    #         _book.add_item(_image_item)

    # async def main():
    #     promises = [add_resource(_resource)
    #                 for _resource in resources]
    #     await asyncio.gather(*promises)

    # asyncio.run(main())
    for _resource in resources:
        """Add resources"""
        if _resource['type'] == 'image_url':
            _image_item = sync_get_resource_image_item(
                _resource['url'],
                _resource['file_name'],
                _resource.get('headers')
            )
            if _image_item:
                # add Image file
                _book.add_item(_image_item)

    """Write epub file"""
    epub.write_epub(_out_fname, _book, {})
    """Get size of file"""
    _size = os.path.getsize(_out_fname)
    """Check if binary response is True"""
    if binary_response == "True":
        """Get content from the file"""
        _data_b64 = binascii.b2a_base64(
            get_content_from_file(_out_fname)
        ).decode('utf-8')
    else:
        _data_b64 = None
    """Delete file"""
    rmfile(_out_fname)
    """Transform name"""
    if not title:
        title = _book.uid
    """Transform data response"""
    _data_response = {
        u"title": title,
        u"epub_title": slugify(title)+".epub",
        u"epub_size": _size,
        u"epub_id": _book.uid,
        u"epub_b64": _data_b64
    }
    """Return epub url reference"""
    return success_response_service(
        data=_data_response
    )


def get_download_from_storage(epub_id):
    """Download a file from storage

    :param epub_id: Id of the epub file, it's the filename
    """
    try:
        """Define out filename"""
        fname = "{0}/{1}.epub".format(
            EPUB_OUT_PATH,
            epub_id
        )
        """Get content from the file"""
        _content = get_content_from_file(fname)
        """Return the data to cliente"""
        return success_response_service(
            data=_content
        )
    except Exception as err:
        return error_response_service(str(err))


def get_content_from_file(fname):
    """Get all content from a file

    :param fname: Name of the file to get information.
    """

    """Open the file"""
    _book = open(fname, "rb")
    """Read the book"""
    _content = _book.read()
    """Close the file"""
    _book.close()
    """Return data"""
    return _content


async def get_resource_image_item(url, file_name, headers={}):
    # load Image file
    _binary_image = await get_download_item_req(url, headers)
    """Check that this one havenot errors"""
    if not _binary_image:
        return None
    # define Image file path in .epub
    _image_item = epub.EpubItem(
        uid=file_name, file_name='images/{0}'.format(file_name), content=_binary_image['binary'])
    return _image_item


async def get_download_item_req(url, headers):
    """Download items asynchronously"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as response:
            _downloaded_item = await response.read()
            if _downloaded_item:
                return {
                    u'binary': _downloaded_item,
                    u'filename': url.split('/')[-1]
                }
            else:
                return None


def sync_get_resource_image_item(url, file_name, headers={}):
    # load Image file

    _binary_image = requests.get(url, headers=headers)
    """Check that this one havenot errors"""
    if _binary_image.status_code != 200:
        return None
    # define Image file path in .epub
    _image_item = epub.EpubItem(
        uid=file_name, file_name='images/{0}'.format(file_name), content=_binary_image.content)
    return _image_item
