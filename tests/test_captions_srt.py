from pytube import YouTube
import pytest
import logging
import os
from pprint import pformat


def test_english_lookup():
    # Captioned video link
    url = ("https://www.youtube.com/watch?v=QRS8MkLhQmM")

    i = None
    yt = YouTube(url)
    captions = list(enumerate(yt.captions.all()))
    logging.debug(f'captions available: {pformat(captions)}')
    for index, c in captions:
        if "English" in str(c):
            i = index
            break
    if i is None:
        logging.debug(f'No Captions found!')
    else:
        logging.debug(f'English captions found at i = {i}')
    assert "English" in str(c)


def test_nocaptions():
    # uses a short 30s wildlife clip
    url = "https://www.youtube.com/watch?v=5DP5I8Gd6wY"
    i = None
    yt = YouTube(url)
    captions = list(enumerate(yt.captions.all()))
    logging.debug(f'captions available: {pformat(captions)}')
    for index, c in captions:
        if "English" in str(c):
            i = index
            break
    if i is None:
        logging.debug(f'No Captions found!')
        assert True
    else:
        assert False

def test_english_only_captions():
    # A video about captions vs subtitles
    url = "https://www.youtube.com/watch?v=xKtdlRnvwqs"

    i = None
    yt = YouTube(url)
    captions = list(enumerate(yt.captions.all()))
    logging.debug(f'captions available: {pformat(captions)}')
    for index, c in captions:
        if "English" in str(c):
            i = index
            break
    if i is None:
        logging.debug(f'No Captions found!')
    else:
        logging.debug(f'English captions found at i = {i}')
    assert "English" in str(c)