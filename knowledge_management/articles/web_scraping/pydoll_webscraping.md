Web Scraping With Pydoll in 2025
Data Journal
Data Journal

Follow
5 min read
·
May 25, 2025
124


3





In this article, I’ll show you how to get started with Pydoll, tackle JavaScript-based websites, and scale your scraping with rotating proxies. Let’s dive in!

What is Pydoll?
Pydoll is a Python-based browser automation library that simplifies web scraping and web automation. Unlike traditional web scraping tools, which rely on browser drivers (such as Selenium’s WebDriver), Pydoll connects directly to Chromium-based browsers via the DevTools Protocol. This eliminates the need for external dependencies, reducing setup complexity and avoiding issues related to driver mismatches.

First released in early 2025, Pydoll has quickly gained popularity due to its unique features and capabilities, making it a solid choice for developers tackling modern web scraping challenges.

Key Features of Pydoll:

Zero Web Drivers: Eliminates the need for browser drivers, avoiding version compatibility issues.
Async-First Architecture: Built on asyncio for high concurrency and low memory usage.
Human-Like Interactions: Simulates realistic mouse movements, typing, and clicking to avoid detection.
Multi-Browser Support: Works with Chrome, Edge, and other Chromium browsers.
Native Cloudflare Bypass: Can bypass Cloudflare’s anti-bot protections automatically.
Proxy Support: Supports IP rotation and geo-targeting using proxies.
Installing and Setting Up Pydoll
Step 1: Install Python
Before you begin, ensure that you have Python 3+ installed on your machine. If not, download it from python.org and follow the installation instructions.

Step 2: Create Your Project Directory
Start by creating a new directory for your project. Open your terminal or command prompt and run the following command:

mkdir pydoll-scraper
cd pydoll-scraper
Step 3: Set Up a Virtual Environment
It’s a good practice to use a virtual environment for your Python projects to avoid conflicts with other Python libraries. To set up a virtual environment, run the following command:

python -m venv venv
Activate the virtual environment:

On macOS/Linux:

source venv/bin/activate

On Windows:

venv/Scripts/activate

Step 4: Install Pydoll
Now that your environment is set up, install Pydoll by running:

pip install pydoll-python

Scraping Data from a Dynamic Website
Now, let’s use Pydoll to scrape data from a dynamic website that loads content using JavaScript.

Step 1: Import Pydoll and Set Up the Browser
In your scraper.py file, start by importing the necessary libraries and initializing Pydoll:

import asyncio
from pydoll.browser.chrome import Chrome
from pydoll.constants import By
import csv

async def main():
    async with Chrome() as browser:
        await browser.start()
        page = await browser.get_page()
        # Navigation and scraping logic goes here

if __name__ == "__main__":
    asyncio.run(main())
Step 2: Navigate to the Website
Let’s scrape data from a website called “Quotes to Scrape.” This site loads quotes dynamically using JavaScript, which traditional scraping tools can’t handle. You can visit the site with the following code:

await page.go_to("https://quotes.toscrape.com/js-delayed/?delay=2000")
Step 3: Wait for Elements to Load
Since the content on this page is rendered with a delay, you need to wait for the elements to appear. Pydoll has a method called wait_element to handle this:

await page.wait_element(By.CSS_SELECTOR, ".quote", timeout=3)
This will ensure that the quotes are loaded before scraping them.

Step 4: Extract the Data
Now that the elements are loaded, we can extract the data. We can loop through all the quote elements and extract the text, author, and tags:

quotes = []
quote_elements = await page.find_elements(By.CSS_SELECTOR, ".quote")
for quote_element in quote_elements:
    text_element = await quote_element.find_element(By.CSS_SELECTOR, ".text")
    # Remove both regular and smart quotes for demo
    text = (await text_element.get_element_text()).replace('"', "").replace("“", "").replace("”", "")
    author_element = await quote_element.find_element(By.CSS_SELECTOR, ".author")
    author = await author_element.get_element_text()
    tag_elements = await quote_element.find_elements(By.CSS_SELECTOR, ".tag")
    tags = [await tag_element.get_element_text() for tag_element in tag_elements]
    quote = {
        "text": text,
        "author": author,
        "tags": tags
    }
    quotes.append(quote)
Step 5: Save the Data to CSV
Finally, export the scraped data to a CSV file:

with open("quotes.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["text", "author", "tags"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for quote in quotes:
        writer.writerow({
            "text": quote["text"],
            "author": quote["author"],
            "tags": ", ".join(quote["tags"])
        })
Bypassing Cloudflare with Pydoll
Cloudflare is a popular web application firewall used by many websites to prevent bots. If you’re scraping a site behind Cloudflare, you will likely encounter CAPTCHAs or other challenges.

Pydoll provides a straightforward way to bypass Cloudflare’s anti-bot protections:

Context Manager Approach
The easiest way to bypass Cloudflare using Pydoll is with the context manager expect_and_bypass_cloudflare_captcha():

async with page.expect_and_bypass_cloudflare_captcha():
await page.go_to("https://www.scrapingcourse.com/antibot-challenge")
This automatically handles the CAPTCHA and allows the scraper to continue.

Background Processing Approach
If you don’t want your script to be blocked while solving the CAPTCHA, use the background processing approach:

await page.enable_auto_solve_cloudflare_captcha()
# Scrape the page while the CAPTCHA is being solved in the background
await page.go_to("https://www.scrapingcourse.com/antibot-challenge")
# Disable CAPTCHA solving when done
await page.disable_auto_solve_cloudflare_captcha()
Integrating Rotating Proxies with Bright Data
To avoid getting blocked by the website’s server, you can use rotating proxies. Bright Data (formerly Luminati) offers one of the largest and most reliable proxy networks.

How to Use Bright Data Proxies
Sign up for a Bright Data account, log in to your dashboard, and obtain your proxy credentials. Once you have them, you can configure Pydoll to use these proxies:

await page.set_proxy({
"host": "brd.superproxy.io",
"port": 33335,
"username": "your_username",
"password": "your_password"
})
Using rotating proxies ensures that each request is made from a different IP address, preventing your scraper from being blocked.

Limitations of Pydoll
While Pydoll is a powerful tool, it’s important to understand its limitations:

Rate Limiting: Even with proxies, you can still be rate-limited if you make too many requests too quickly. It’s important to implement strategies like randomizing delays between requests.
CAPTCHA: While Pydoll can bypass Cloudflare, it might not always work for every type of CAPTCHA. Therefore, I suggest you go over my list of the best CAPTCHA solvers (all tested!).
Compatibility: Pydoll is designed for Chromium-based browsers, so it may not work with all web pages, particularly those requiring non-Chromium browsers.
Alternatives to Pydoll
If Pydoll doesn’t suit your needs, there are several alternatives you can explore:

Selenium: The most popular web scraping tool, offering full browser automation. It supports all browsers but requires browser drivers.
Playwright: A modern alternative to Selenium, designed for speed and reliability with support for Chromium, Firefox, and WebKit.
Scrapy: A powerful Python framework for large-scale web scraping, but it doesn’t handle JavaScript-heavy sites out of the box.
Conclusion
Pydoll is a powerful tool that simplifies web scraping in 2025. Its asynchronous architecture, ability to handle JavaScript-heavy websites, and built-in Cloudflare bypass make it an excellent choice for modern scraping tasks. By following this step-by-step guide, you can easily set up and deploy a web scraper to gather data from dynamic websites and overcome common challenges like IP blocking and CAPTCHA.

Remember to always respect the legal and ethical considerations of web scraping, and use rotating proxies and delays to avoid overwhelming target servers. Happy scraping!

