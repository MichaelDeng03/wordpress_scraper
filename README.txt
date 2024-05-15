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