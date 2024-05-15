"""
Author: Michael Deng @michaeldeng2003@gmail.com
Date: 2021-03-13
Helper functions for scraping techcrunch articles.
"""
import requests
# bs4 not allowed, only requests
import re
import pandas as pd
import html as html_parser


def find_title(html):
    """
    Finds the title of a given techcrunch wordpress article
    :param html: html to parse
    :return: String containing title, None if not found
    """
    # Most articles are optimized with Yoast, and have a metatag with the title
    # Note, also the <title> tag, but this is appended with | TechCrunch and is not displayed on the page
    title_start = html.find('<meta property="og:title" content="')
    if title_start != -1:
        title_start += len('<meta property="og:title" content="')
        title_end = html.find('"', title_start)
        title = html[title_start:title_end]

    # If not, we can find the title in the article body.
    title_start = html.find('<h1 class="article__title">')
    if title_start != -1:
        title_start += len('<h1 class="article__title">')
        title_end = html.find('</h1>', title_start)
        title = html[title_start:title_end]

    if title:
        return html_parser.unescape(title)
    return None


def find_author(html):
    """
    Finds the author of a given techcrunch wordpress article
    :param html: html to parse
    :return: String containing author, None if not found
    """
    # Most articles are optimized with Yoast, and have a metatag with the author
    author_start = html.find('<meta name="author" content="')
    if author_start != -1:
        author_start += len('<meta name="author" content="')
        author_end = html.find('"', author_start)
        author = html[author_start:author_end].strip()

    # If not, we can find the author in the article body.
    author_start = html.find('<div class="article__byline">')
    if author_start != -1:
        # Usually there will be a link to the author's page followed by their name
        author_url = re.search(
            '<a href="https://techcrunch.com/author/.+', html[author_start:])
        # If there is text after url, then use that name, otherwise use the url
        end_author_url = author_url.span()[1]
        end_author_tag = html[author_start:].find('</a>', end_author_url)
        author = html[author_start:][end_author_url:end_author_tag].strip()
        if author == '':
            author = author_url.split('/')[-1]
            author = author.replace('-', ' ').capitalize()

    if author:
        return html_parser.unescape(author)

    return None


def find_datetime(html):
    """
    Finds the datetime of a given techcrunch wordpress article
    :param html: html to parse
    :return: String containing datetime, None if not found
    """
    # Most articles are optimized with Yoast, and have a metatag with the datetime
    datetime_start = html.find(
        '<meta property="article:published_time" content="')
    if datetime_start != -1:
        datetime_start += len('<meta property="article:published_time" content="')
        datetime_end = html.find('"', datetime_start)
        return html[datetime_start:datetime_end]

    # If not, we can find the datetime in the article body.
    datetime_start = html.find('<time class="article__published" datetime="')
    if datetime_start != -1:
        datetime_start += len('<time class="article__published" datetime="')
        datetime_end = html.find('"', datetime_start)
        return html[datetime_start:datetime_end]

    return None


def is_article(html):
    """
    Checks if the page is an article
    :param html: html to parse
    :return: True if article, False if not
    """
    # If yoast categorized it as an article, it is an article
    if html.find('<meta property="og:type" content="article" />'):
        return True

    # If the page has a title, it is an article
    if find_title(html) is not None:
        return True

    # If the page has an <article> tag, it is an article
    if html.find('<article'):
        return True

    return False


def find_article_text(html):
    """
    Finds the article text of a given techcrunch wordpress article
    :param html: html to parse
    :return: String containing article text. None if not found"""
    # Article starts at article content. Article itself may have nested divs, so skip over them to find the end of the div
    article_start = html.find('<div class="article-content">')
    if article_start:
        next_start = html.find('<div', article_start + 1)
        next_end = html.find('/div>', article_start + 1)
        while True:
            if next_start < next_end:
                next_start = html.find('<div', next_end)
                next_end = html.find('/div>', next_end + 1)
            else:
                article_end = next_end
                break
        article_text = html[article_start:article_end-1]
        # Some articles have bylines within the article content. We don't want to include these. Only text within a p tag should be included

        # Split by paragraph end
        article_text = article_text.split('</p>')
        article_text_temp = [text.strip() for text in article_text]
        article_text = []

        for paragraph in article_text_temp:
            # Remove all html tags using regex. Everything between <> that doesn't include <> is removed
            tag = '<[^<>]*>'
            while re.search(tag, paragraph):
                paragraph = re.sub(tag, '', paragraph).strip()
            article_text.append(paragraph)

        article_text = '\n'.join(article_text)
        article_text = html_parser.unescape(article_text)
        return article_text
    return None


def find_links_in_article(html):
    """
    Finds all links in the article
    :param html: html to parse
    :return: String of links in the article separated by tab, empty list if none found, and None if can't find article
    """
    article_start = html.find('<div class="article-content">')
    if article_start:
        # Find html for the start of the article
        next_start = html.find('<div', article_start + 1)
        next_end = html.find('/div>', article_start + 1)
        while True:
            if next_start < next_end:
                next_start = html.find('<div', next_end)
                next_end = html.find('/div>', next_end + 1)
            else:
                article_end = next_end
                break
        article_text = html[article_start:article_end-1]

        # Split by paragraph end to make parsing easier
        article_text = article_text.split('</p>')
        article_text = [text.strip() for text in article_text]

        # Find the links using regex.
        links = []
        for paragraph in article_text:
            # Find all tags that start with <a and end with </a> (find href later)
            tag = '<a[^<>]*>'
            matches = re.findall(tag, paragraph)
            for match in matches:
                # Find the href in the tag
                href = re.search('href="[^"]+"', match)
                if href:
                    href = href.group()
                    href = href[6:-1]
                    links.append(href)
        return '\t'.join(links)
    return None


def find_article_links(html):
    """
    Finds all links in the article which have the same format as techcrunch articles
    :param html: html to parse
    :return: List of links to techcrunch articles found on this page, empty list if none found
    """
    links = []
    tag = '<a[^<>]*>'
    matches = re.findall(tag, html)
    for match in matches:
        for match in matches:
            # Remove escape characters
            match = match.replace('\\', '')
            # Find the href in the tag
            href = re.search('href="[^"]+"', match)
            if href:
                href = href.group()
                href = href[6:-1]
                links.append(href)

    links = [link.strip() for link in links if re.search(
        'https://techcrunch.com/\d{4}/\d{2}/\d{2}/', link)]
    links = list(set(links))
    return links


def scrape(url, use_local=False, write_to_file=False):
    """
    Scrape the contents of a wordpress (techcrunch) article
    :param url: url of the article
    :param use_local: If true, use local file instead of requesting from url
    :param write_to_file: If true, write the html to a file
    :return: dataframe holding relevant information such as title, author, date published, article text, and a list of urls on that page (df, urls)
    """
    if not use_local:
        try:
            r = requests.get(url)
            r.raise_for_status()
            html = r.text
        except requests.exceptions.RequestException as e:
            print('Error Message: ', e)
            print('Request failed, returning none')
            return None, None
    else:
        with open('techcrunch.html', 'r') as f:
            html = f.read()

    if write_to_file:
        with open('techcrunch.html', 'w') as f:
            f.write(html)

    if is_article(html):
        title = find_title(html)
        author = find_author(html)
        datetime = find_datetime(html)
        article_text = find_article_text(html)
        links_in_article = find_links_in_article(html)
        df = pd.DataFrame({'link': url, 'title': title, 'author': author,
                           'datetime': datetime, 'article_text': article_text, 'links_in_article': links_in_article}, index=[0])

        # At this point, we have most of the relevant information about the article. But we need more articles to scrape
        # from. So we need to find all the links on the page, and return all which follow the form of a techcrunch article url.
        article_links = find_article_links(html)

        return df, article_links
    else:
        return None, None

