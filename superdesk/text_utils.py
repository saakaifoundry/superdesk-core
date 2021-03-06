
# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2017 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import re
from lxml import etree  # noqa
from superdesk import etree as sd_etree
from lxml import html as lxml_html
from lxml.html import clean


# This pattern matches http(s) links, numbers (1.000.000 or 1,000,000 or 1 000 000), regulars words,
# compound words (e.g. "two-done") or abbreviation (e.g. D.C.)
WORD_PATTERN = re.compile(r'https?:[^ ]*|([0-9]+[,. ]?)+|([\w]\.)+|[\w][\w-]*')


def get_text_word_count(text):
    """Get word count for given plain text.

    :param str text: text string
    :return int: word count
    """
    return sum(1 for word in WORD_PATTERN.finditer(text))


def get_text(markup, content='xml', lf_on_block=False, space_on_elements=False):
    """Get plain text version of (X)HTML or other XML element

    if the markup can't be parsed, it will be returned unchanged
    :param str markup: string to convert to plain text
    :param str content: 'xml' or 'html', as in parse_html
    :param bool lf_on_block: if True, add a line feed on block elements' tail
    :param bool space_on_elements: if True, add a space on each element's tail
        mainly used to count words with non HTML markup
    :return str: plain text version of markup
    """
    try:
        root = sd_etree.parse_html(
            markup,
            content=content,
            lf_on_block=lf_on_block,
            space_on_elements=space_on_elements)
        text = etree.tostring(root, encoding='unicode', method='text')
        return text
    except etree.ParseError:
        return markup


def get_word_count(markup, no_html=False):
    """Get word count for given html.

    :param str markup: xhtml (or other xml) markup
    :param bool no_html: set to True if xml param is not (X)HTML
        if True, a space will be added after each element to separate words.
        This avoid to have construct like <hl2>word</hl2><p>another</p> (like in NITF)
        being counted as one word.
    :return int: count of words inside the text
    """
    if no_html:
        return get_text_word_count(get_text(markup, content='xml', space_on_elements=True))
    else:
        return get_text_word_count(get_text(markup, content='html', lf_on_block=True))


def get_char_count(html):
    """Get character count for given html.

    :param html: html string to count
    :return int: count of chars inside the text
    """
    return len(get_text(html))


def get_reading_time(word_count):
    """Get estimanted number of minutes to read a text

    Check https://dev.sourcefabric.org/browse/SDFID-118 for details
    :param int word_count: number of words in the text
    :return int: estimated number of minute to read the text
    """
    reading_time_float = word_count / 250
    reading_time_minutes = int(reading_time_float)
    reading_time_rem_sec = int((reading_time_float - reading_time_minutes) * 60)
    if reading_time_rem_sec >= 30:
        reading_time_minutes += 1
    return reading_time_minutes


def sanitize_html(html):
    """Sanitize HTML

    :param str html: unsafe HTML markup
    :return str: sanitized HTML
    """
    if not html:
        return ""

    blacklist = ["script", "style", "head"]

    root_elem = lxml_html.fromstring(html)
    cleaner = clean.Cleaner(
        add_nofollow=False,
        kill_tags=blacklist
    )
    cleaned_xhtml = cleaner.clean_html(root_elem)

    safe_html = etree.tostring(cleaned_xhtml, encoding="unicode")

    # the following code is legacy (pre-lxml)
    if safe_html == ", -":
        return ""

    return safe_html
