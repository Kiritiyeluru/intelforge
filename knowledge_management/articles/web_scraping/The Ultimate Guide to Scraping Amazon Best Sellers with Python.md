Manually tracking prices and items can be difficult. That’s where web scraping comes in. Instead of writing everything down, I can automate this process using Python. By scraping the Best Sellers page, I can gather data in formats like CSV, making it easy to analyze and track trends. Let’s dive into how to scrape Amazon’s Best Sellers with Python.

What are Amazon Best Sellers?
Amazon Best Sellers Rank (BSR) is a system that ranks products based on their sales volume. This rank helps customers find the top-selling products in various categories and view the sales position of items they’re considering. The BSR is displayed on each product page and updated regularly to reflect current trends.

Scraping Best Sellers pages is similar to scraping any other Amazon product page. However, Amazon has security measures that make it challenging to access this data quickly. If you send too many requests, Amazon can block your IP address. To avoid this, you must add safety measures to your Python code. Managing this challenge is crucial to successful web scraping on Amazon.

The Best Amazon Scraping Tools
Before we jump into the step-by-step manual scraping guide, I strongly suggest checking out my top 5 Amazon scrapers. I am not affiliated with any of the mentioned brands and I review those based on my and my team’s personal experience.

In a hurry? Here is a TL;DR list:

Bright Data: Advanced Amazon scraping with anti-detection and global proxies.
Oxylabs: Specialized e-commerce scraping with localization features.
Smartproxy: API and proxy solutions with rotating IP support.
Zyte: E-commerce scraper with customizable selectors and APIs.
ScraperAPI: Supports multiple languages with flexible, credit-based plans.
Setting Up Your Python Environment for Scraping
We need to set up the necessary Python libraries to start scraping Amazon Best Sellers. We will use Selenium for browser automation, webdriver-manager for managing web drivers, and pandas to store the scraped data in a CSV file.

Step 1: Install Python
First, make sure you have Python installed on your machine. You can download it from the official Python website.

Next, open a terminal or command prompt and install the necessary dependencies:

pip install selenium webdriver-manager pandas
Step 2: Inspecting Amazon’s Best Sellers Page
Before we can start scraping, we need to understand the structure of the Amazon Best Sellers page. Open any Amazon Best Sellers page in your browser and use the “Inspect” tool (right-click on any element and select “Inspect”) to explore the HTML.

For this tutorial, we’ll scrap the “Kitchen & Dining” Best Sellers page. The structure of the page includes:

Product title: The product title is located within a specific HTML element with a class that uniquely identifies it.
Product price: The price is located within another specific HTML element.
Product URL: Each product has a URL linking to its detailed product page.
These elements will serve as the basis for our scraping efforts.

Step 3: Setting Up Selenium for Web Scraping
To scrape Amazon, we will use Selenium to interact with the Best Sellers page and extract the necessary information.

First, import the required libraries:

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
Next, create a function to initialize the Chrome driver. This function sets up a headless Chrome browser (a browser that runs in the background without displaying a graphical user interface):

def init_chrome_driver():
chrome_options = Options()
chrome_options.add_argument(" - headless")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
return driver
Step 4: Writing the Scraping Logic
We need a function that loads the Best Sellers page and scrapes the product data (title, price, and URL). The following function will do that:

def get_products_from_page(url, driver):
driver.get(url)
time.sleep(3) # Wait for the page to load
# Find all products on the page
product_elements = driver.find_elements(By.CLASS_NAME, "zg-item")
# List to store product data
products = []
# Loop through the products and extract data
for product in product_elements:
try:
title = product.find_element(By.CLASS_NAME, "p13n-sc-truncate").text
url = product.find_element(By.CLASS_NAME, "a-link-normal").get_attribute("href")
price = product.find_element(By.CLASS_NAME, "p13n-sc-price").text
products.append({"title": title, "url": url, "price": price})
except Exception as e:
print(f"Error extracting product data: {e}")
continue
return products
This function takes the URL of the Best Sellers page and the Selenium driver as inputs. It then extracts each product’s title, price, and URL on the page and stores them in a list.

Step 5: Exporting Data to CSV
Once we have the data, we can save it in a CSV file using Pandas:

def save_to_csv(products, filename):
df = pd.DataFrame(products)
df.to_csv(filename, index=False)
This function converts the list of product data into a Pandas DataFrame and saves it as a CSV file.

Step 6: Putting It All Together
Now, we can combine everything into a main function that initiates the web scraping process:

def main():
url = "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/"
driver = init_chrome_driver()
try:
products = get_products_from_page(url, driver)
save_to_csv(products, "amazon_best_sellers.csv")
finally:
driver.quit()
if __name__ == "__main__":
main()
Step 7: Running the Script
To run the script, simply execute the Python file in your terminal:

python main.py
After running the script, a file named amazon_best_sellers.csv will be generated in your working directory containing the scraped product data.

Step 8: Handling Scraping Challenges
While the above script works, scraping Amazon is not without challenges. Amazon employs anti-scraping techniques such as:

Rate-limiting: Amazon can block your IP address if it detects too many requests in a short period. To avoid this, implement a delay between requests using time.sleep().
CAPTCHA: Amazon uses CAPTCHAs to prevent bots from scraping their site. Selenium cannot solve CAPTCHAs, so you may need a service like 2Captcha to bypass them.
IP blocking: To prevent your IP from being blocked, consider using a proxy service like ScraperAPI or rotating IP addresses.
Step 9: Scraping More Categories
The script can be easily modified to scrape Best Sellers pages from other categories. Simply replace the URL in the main() function with the category URL you wish to scrape.

For example, to scrape the “Books” Best Sellers page, change the URL to:

url = "https://www.amazon.com/Best-Sellers-Books/zgbs/books/"
Step 10: Using an Amazon Scraping API (Alternative Method)
If you encounter too many challenges with traditional web scraping, you can use an Amazon Scraping API. These APIs provide a simpler and more reliable way to collect data from Amazon.

For example, the Amazon Best Sellers Scraper API allows you to scrape Best Sellers data without worrying about IP blocks or CAPTCHAs. Here’s an example of how to use it:

import requests
def scrape_amazon_api():
payload = {
"source": "amazon_bestsellers",
"domain": "com",
"query": "284507",
"render": "html",
"start_page": 1,
"parse": True,
}
response = requests.post("https://realtime.oxylabs.io/v1/queries", json=payload, auth=("USERNAME", "PASSWORD"))
data = response.json()
# Process the data and save it to CSV
products = data["results"][0]["content"]["results"]
df = pd.DataFrame(products)
df.to_csv("amazon_products_api.csv", index=False)
scrape_amazon_api()
Conclusion
Scraping Amazon Best Sellers pages using Python provides a valuable way to gather product data for research, analysis, and competitive intelligence. While traditional web scraping methods using Selenium can be effective, they come with challenges like rate-limiting and CAPTCHAs. To overcome these obstacles, you can implement advanced techniques like rotating proxies or use specialized scraping APIs designed for large-scale data collection.

Got any questions? Waiting for them in the comments :)