In this tutorial, we’ll walk you through how to get started with Scrapy for web scraping and build your first scraping project.

Why Use Scrapy?
Scrapy is fast, efficient, and highly customizable. It’s especially useful for large-scale scraping projects where you must crawl hundreds or thousands of pages. The framework is built for performance, handling HTTP requests and parsing responses concurrently.

Alternatives to Scrapy
If you are looking for Scrapy alternatives, I can recommend 3 of the top web scraping providers in the industry (I am not affiliated with any of them, don’t worry):

Bright Data: Leading tool with extensive proxy network and solutions.
Oxylabs: Advanced data gathering with reliable proxies and APIs.
Zyte: User-friendly scraping with smart extraction and support.
Key Features of Scrapy:
Built-in support for handling requests: Makes handling multiple pages and links simple.
Concurrency and asynchronous I/O: Efficient handling of multiple requests at once.
Support for XPath and CSS selectors: Powerful ways to navigate through HTML and extract data.
Robust API: Allows you to define how data is handled and stored.
Prerequisites
Basic Python Knowledge: Understanding Python fundamentals is key.
Install Scrapy: Use pip install scrapy to get started. Make sure you have Python 3.6+ installed.
Getting Started with Scrapy
Setting Up Scrapy
To begin using Scrapy, you’ll need to install it. The simplest way to do This is to use pip, Python’s package manager.

pip install scrapy
Once installed, verify the installation by typing the following command:

scrapy version
If Scrapy is installed correctly, this command will return the Scrapy version number.

Creating a Scrapy Project
Scrapy operates around the concept of projects. To create your first project, navigate to the directory where you want your project to reside and run:

scrapy startproject myproject
This will create a folder with the name myproject, containing all the essential files to get started.

Understanding the Project Structure
After creating the project, you’ll notice a folder structure like this:

myproject/
scrapy.cfg # Configuration file
myproject/
__init__.py
items.py # Define the data structure
middlewares.py # Handle middleware logic
pipelines.py # Store the scraped data
settings.py # Project settings
spiders/ # Folder to store your spiders
items.py: Defines the structure of the data you want to scrape.
middlewares.py: Allows you to modify requests and responses.
pipelines.py: Processes and saves the scraped data.
settings.py: Configures your Scrapy project’s behavior.
spiders/: Contains the spider code where all scraping logic will reside.
Writing Your First Spider
A spider is a class in Scrapy that defines how a particular website or a group of websites should be scraped.

Creating a Spider

To create a spider, navigate to the spiders directory and create a new Python file. Let’s call it quotes_spider.py to scrape data from the famous quotes.toscrape.com website, which is great for beginners.

Here’s a basic structure for your spider:

import scrapy
class QuotesSpider(scrapy.Spider):
name = "quotes"
start_urls = ['http://quotes.toscrape.com']
def parse(self, response):
for quote in response.css('div.quote'):
yield {
'text': quote.css('span.text::text').get(),
'author': quote.css('span small::text').get(),
'tags': quote.css('div.tags a.tag::text').getall(),
}
next_page = response.css('li.next a::attr(href)').get()
if next_page is not None:
yield response.follow(next_page, self.parse)
Let’s break this down:

name: This is the spider’s name. Scrapy uses this name to identify which spider to run.
start_urls: This is a list of URLs from which the spider will start scraping.
parse(): This method is where the extraction logic resides. It defines how the content of the page is processed. Here, we’re using CSS selectors (response.css) to extract the text, author, and tags of quotes.
Pagination: After processing the current page, the spider looks for the next page’s URL and follows it to scrape the next set of quotes.
Running the Spider

To run your spider, simply use the following command:

scrapy crawl quotes
Scrapy will visit the starting URL, extract the data, follow links to the next pages, and scrape additional quotes.

Exporting Scraped Data
Scrapy makes it easy to export the scraped data. You can export data in JSON, CSV, or XML formats. To export data to a JSON file, use this command:

scrapy crawl quotes -o quotes.json
This command will save the scraped data into quotes.json. Similarly, you can export it in CSV by changing the extension.

Dealing with Scrapy Settings
Scrapy’s behavior can be configured through the settings.py file. Here are some important settings you may want to adjust:

USER_AGENT: Some websites block requests that don’t have a user agent. You can set your spider’s user agent in the settings.
USER_AGENT = ‘myproject (+http://www.yourdomain.com)'

CONCURRENT_REQUESTS: This setting defines how many requests Scrapy should make concurrently.
CONCURRENT_REQUESTS = 16

DOWNLOAD_DELAY: You can use a delay between requests to avoid overwhelming the server.
DOWNLOAD_DELAY = 1 # 1 second delay between requests

Handling Dynamic Content
Many modern websites use JavaScript to load content dynamically, and Scrapy by itself cannot execute JavaScript. In such cases, you can use Scrapy-Splash or integrate Scrapy with a headless browser like Selenium.

Using Scrapy-Splash
Splash is a headless browser designed for web scraping. To use it, you need to install it and then integrate it with Scrapy.

Here’s how to install Scrapy-Splash:

pip install scrapy-splash
You also need to update the settings.py file to include:

DOWNLOADER_MIDDLEWARES = {
'scrapy_splash.SplashCookiesMiddleware': 723,
'scrapy_splash.SplashMiddleware': 725,
'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}
SPIDER_MIDDLEWARES = {
'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
By integrating Splash, Scrapy can handle dynamic content better and fetch data from JavaScript-based websites.

Scrapy Pipelines: Storing the Data
Once you’ve scraped your data, you’ll need a way to store or process it. This is where pipelines come into play.

Let’s say you want to store the scraped data in a MongoDB database. First, install the pymongo library:

pip install pymongo
Then, create a pipeline in pipelines.py:

import pymongo
class MongoPipeline:
def open_spider(self, spider):
self.client = pymongo.MongoClient("mongodb://localhost:27017/")
self.db = self.client["scrapy_db"]
def close_spider(self, spider):
self.client.close()
def process_item(self, item, spider):
self.db["quotes"].insert_one(dict(item))
return item
Don't forget to activate the pipeline in settings.py:
ITEM_PIPELINES = {
'myproject.pipelines.MongoPipeline': 300,
}
Now, all your scraped data will be stored in a MongoDB collection.

Conclusion
Web scraping with Scrapy is a powerful way to extract data from websites efficiently. From setting up Scrapy, creating spiders, handling dynamic content, and storing the data in a database, Scrapy offers flexibility for beginners and experienced developers.

Mastering Scrapy can automate your data collection processes, giving you the tools to gather valuable insights and drive industry decision-making.

Now that you understand how Scrapy works build your next web scraping project!