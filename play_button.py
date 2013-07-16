# -*- mode: Python ; coding: utf-8 -*-
# Copyright © 2013 Roland Sieker <ospalh@gmail.com>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/copyleft/agpl.html

"""Add-on for Anki 2 to add AnkiDroid-style replay buttons."""

from PyQt4.QtCore import QUrl
from PyQt4.QtGui import QDesktopServices
import os
import re
import shutil

from anki.hooks import addHook, wrap
from anki.sound import play
from aqt import mw
from aqt.browser import Browser
from aqt.clayout import CardLayout
from aqt.reviewer import Reviewer
from aqt import mw

__version__ = "1.2.0"

sound_re = ur"\[sound:(.*?)\]"

original_arrow_name = 'replay.png'
collection_arrow_name = '_inline_replay_button.png'


def play_button_filter(qa_html, qa_type, dummy_fields, dummy_model,
                       dummy_data, dummy_col):
    u"""
    Filter the questions and answers to add play buttons.
    """

    def add_button(sound):
        u"""
        Add img link after the match.

        Add an img link after the match to replay the audio. The title
        is set to "Replay" on the question side to hide information or
        to the file name on the answer.
        """
        if 'q' == qa_type:
            title = u"Replay"
        else:
            title = sound.group(1)
        return u"""{orig}<a href='javascript:py.link("ankiplay{fn}");' \
title="{ttl}"><img src="{ip}" alt="play" style="max-width: 32px; \
max-height: 1em; min-height:8px;" class="replaybutton browserhide">\
</a>""".format(
            orig=sound.group(0), fn=sound.group(1), ip=collection_arrow_name,
            ttl=title)
    return re.sub(sound_re, add_button, qa_html)


def review_link_handler_wrapper(reviewer, url):
    u"""Play the sound or call the original link handler."""
    if url.startswith("ankiplay"):
        play(url[8:])
    else:
        original_review_link_handler(reviewer, url)


def simple_link_handler(url):
    u"""Play the file."""
    if url.startswith("ankiplay"):
        play(url[8:])
    else:
        QDesktopServices.openUrl(QUrl(url))


def add_clayout_link_handler(clayout, dummy_t):
    u"""Make sure we play the files from the card layout window."""
    clayout.forms[-1]['pform'].frontWeb.setLinkHandler(simple_link_handler)
    clayout.forms[-1]['pform'].backWeb.setLinkHandler(simple_link_handler)


def add_preview_link_handler(browser):
    u"""Make sure we play the files from the preview window."""
    browser._previewWeb.setLinkHandler(simple_link_handler)


def copy_arrow():
    u"""Copy the image file to the collection."""
    if not os.path.exists(os.path.join(
            mw.col.media.dir(), collection_arrow_name)):
        shutil.copy(
            os.path.join(mw.pm.addonFolder(), 'color_icons',
                         original_arrow_name),
            collection_arrow_name)


original_review_link_handler = Reviewer._linkHandler
Reviewer._linkHandler = review_link_handler_wrapper

addHook("mungeQA", play_button_filter)
Browser._openPreview = wrap(Browser._openPreview, add_preview_link_handler)
CardLayout.addTab = wrap(CardLayout.addTab, add_clayout_link_handler)
addHook("profileLoaded", copy_arrow)
