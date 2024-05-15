"""
Author: Michael Deng @michaeldeng2003@gmail.com
Date: 2021-03-13
The both wordpress_scraper file has a scraping method which takes a techcrunch article url, and return pandas dataframes with relevant article information. 
The driver concatenates returned dataframes, and saves it to 'articles.csv'.
A limited number of fields are considered, currently limited to:
Link to article
Title
Author
Date/Time published 
Article contents
Links in article (string separated by \t)

Future Improvements:
Article text currently contains all text in div class article-content. However, sometimes there is additional information in there besides the article text. For example, article/contributor bylines. 
There are many more fields which may be relevant, author social media (ie twitter), images on the page, speakable summary.
Further independence from meta data included by Yoast. 
Consider existing stored articles so that we don't have to process them again.
"""

import wordpress_scraper
import pandas as pd


def main(num_articles=50, starter_url='https://techcrunch.com/2023/03/13/etsy-processing-seller-payments-alternative-partners-after-svb-implosion/'):
    """
    This driver script will scrape the first 50 articles from techcrunch.com starting from a given url, 
    and going to other articles linked in each subsequent article
    """
    urls = [starter_url]
    seen_urls = set()

    df_articles = pd.DataFrame(
        columns=['link', 'title', 'author', 'datetime', 'article_text', 'links_in_article'])
    
    while urls and len(df_articles) < num_articles:
        url = urls.pop(-1)
        while url in seen_urls:
            url = urls.pop(-1)  # pop from end because suddenly runtime matters lol
        seen_urls.add(url)

        print(f'Scraping from {url}')
        df, article_urls = wordpress_scraper.scrape(url)
        
        if df is not None:
            df_articles = pd.concat((df_articles, df), join='inner')

        urls.extend(article_urls)

    if len(df_articles) < num_articles:
        print(f'Warning: only {len(df_articles)} articles found. Saving to articles.csv anyway')
    with open('articles.csv', 'w') as f:
        f.write(df_articles.to_csv(index=False))


main()
