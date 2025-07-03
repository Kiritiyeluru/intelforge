Throttling limits the number of requests, protecting the server from getting overwhelmed by high traffic. It’s like setting a speed limit so no one can flood the application with too many calls simultaneously. Doing this allows me to maintain stability and give every user a fair experience.

In this article, I’ll explore several methods for throttling requests, explain how to implement them, and highlight why they matter in modern software development and web scraping.

Why Throttle Requests?
Before exploring how to throttle requests, it is essential to understand why throttling is necessary. Some of the main reasons include:

Server Load Management: When too many requests are made quickly, the server may become overloaded and degrade user performance.
Fair Usage: It is key to ensure all users get a fair share of the server’s resources. A few clients could monopolize resources without throttling, leading to unfair distribution.
Preventing Abuse: Bad actors might abuse APIs by making excessive requests, intentionally or unintentionally. Throttling helps prevent such abusive behaviors.
Cost Management: For services billed based on the number of requests (such as many cloud platforms), throttling helps limit costs by controlling the frequency of requests.
Automated Solutions
if web scraping is your use case, using one of these tools will automate the whole throttling process for you, so you won’t have to do anything:

Bright Data: Powerful proxy-based scraping for complex needs.
ScraperAPI: Affordable, multi-language support for unprotected sites.
Oxylabs: High-quality proxies, AI-based data parsing.
ScrapingBee: Handles challenging sites with CAPTCHA solving.
I am not affiliate with any of the providers, these are just tools that me and my team are using frequently.

Basic Concepts of Request Throttling
Request throttling can be implemented at different levels: client-side (before sending the requests) and server-side (while processing the requests). There are several popular approaches to throttle requests:

Rate Limiting: Allowing a fixed number of requests within a specific period.
Leaky Bucket Algorithm: Limiting how quickly requests are processed.
Token Bucket Algorithm: Providing clients with tokens representing requests they can make.
Exponential Backoff: Slowing down the rate of requests exponentially to reduce server stress.
Each method has its strengths, depending on the use case and the architecture of the service.

Throttling Techniques
Rate Limiting
Rate Limiting is the simplest and most common form of request throttling. It caps the number of requests made within a specific time window.

For example, if an API only allows 100 requests per minute per client, the rate limiter will reject requests exceeding that limit until the next minute begins.

Implementation: This technique often uses middleware or built-in functionalities of frameworks such as Flask or Express.js.

from flask import Flask, request
from time import time
app = Flask(__name__)
rate_limit_window = 60 # 60 seconds
max_requests = 100
user_requests = {}
@app.route('/api')
def my_api():
current_time = time()
user_ip = request.remote_addr
if user_ip not in user_requests:
user_requests[user_ip] = []
# Remove outdated requests
user_requests[user_ip] = [req for req in user_requests[user_ip] if current_time - req < rate_limit_window]
if len(user_requests[user_ip]) >= max_requests:
return "Too many requests, please try again later.", 429
# Record new request
user_requests[user_ip].append(current_time)
return "Hello, World!"
In the example above, a sliding window rate limiter ensures that users do not exceed the limit of 100 requests in a 60-second window.

Leaky Bucket Algorithm
The Leaky Bucket Algorithm is another popular approach to throttling requests. Imagine a bucket with a hole at the bottom. Water is poured into the bucket, and it leaks out constantly. When the bucket is full, any additional water will overflow.

In request throttling, the bucket is filled with incoming requests, and the server processes them at a fixed rate. If the rate of incoming requests exceeds the rate the server can handle, the excess requests will be dropped.

This approach helps smooth out sudden spikes in requests and keeps the server processing load steady.

Implementation: The Leaky Bucket Algorithm can queue requests and process them consistently.

import queue
import threading
import time
leaky_bucket = queue.Queue(maxsize=10) # Limit the number of items that can be queued
def process_request():
while True:
request = leaky_bucket.get()
if request is None:
break
print(f"Processing request {request}")
time.sleep(1) # Simulate processing time
leaky_bucket.task_done()
# Worker thread to process requests
threading.Thread(target=process_request, daemon=True).start()
# Adding requests to the bucket
for i in range(20):
if not leaky_bucket.full():
leaky_bucket.put(f"Request {i}")
else:
print(f"Request {i} was dropped due to throttling")
This implementation allows bursts of requests when tokens are available, which can be useful for use cases where temporary spikes in demand must be handled gracefully.

Exponential Backoff
Exponential Backoff is another throttling approach commonly used to handle API retries. Instead of making requests continuously, the client increases the delay between subsequent retry attempts. This helps prevent overloading the server during congestion.

Use Case: It’s frequently used when a service temporarily returns a “Too Many Requests” (HTTP 429) or similar error.

import time
def exponential_backoff():
attempt = 0
max_attempts = 5
while attempt < max_attempts:
try:
# Simulate API call
print(f"Attempt {attempt + 1}")
raise Exception("API limit reached")
except Exception as e:
print(e)
attempt += 1
delay = 2 ** attempt
print(f"Retrying in {delay} seconds…")
time.sleep(delay)
# Call the function
exponential_backoff()
The exponential backoff here ensures that requests become less frequent after each failure, eventually giving the server some breathing space.

Server-Side vs. Client-Side Throttling
While the above techniques mainly illustrate server-side throttling, it’s important to consider client-side throttling.

Client-Side Throttling
Client-side throttling helps manage the number of requests the client sends before they even reach the server. This helps avoid denial-of-service errors before they even occur.

For instance, a JavaScript client calling a public API can implement throttling to ensure the user’s browser doesn’t overload the API endpoint.

function throttle(func, limit) {
let lastFunc;
let lastRan;
return function () {
const context = this;
const args = arguments;
if (!lastRan) {
func.apply(context, args);
lastRan = Date.now();
} else {
clearTimeout(lastFunc);
lastFunc = setTimeout(function () {
if (Date.now() - lastRan >= limit) {
func.apply(context, args);
lastRan = Date.now();
}
}, limit - (Date.now() - lastRan));
}
};
}
// Example usage
const makeApiCall = () => console.log("API request sent");
window.addEventListener("resize", throttle(makeApiCall, 2000));
The above JavaScript code defines a throttling function to limit the frequency with which an API request is triggered in response to an event like window resizing.

Popular Tools and Frameworks
Nginx Rate Limiting
Nginx is a popular web server with built-in capabilities to handle rate limiting using the limit_req_zone directive. This helps to throttle requests at the web server level before they even reach the application layer.

http {
limit_req_zone $binary_remote_addr zone=one:10m rate=5r/s;
server {
location /api {
limit_req zone=one burst=10 nodelay;
proxy_pass http://backend_server;
}
}
}
WS API Gateway
AWS API Gateway also offers built-in rate limiting capabilities to throttle requests to the endpoints it manages, helping developers control usage and prevent abuse.

Best Practices for Throttling Requests
Graceful Error Handling: Clients should gracefully handle errors, particularly those related to throttling (e.g., HTTP status code 429). Implementing retry logic with exponential backoff is often a good idea.
Dynamic Throttling: Adjust throttling limits based on resource availability or time of day. For instance, reduce limits during peak times to ensure consistent user performance.
Monitoring and Alerts: Always monitor request volumes and set alerts for suspicious spikes, which could indicate potential abuse or misconfiguration in client applications.
User-Based and IP-Based Limits: Implement different types of rate limits, such as user-based and IP-based, to better control the flow of requests across multiple access points.
Conclusion
Request throttling is a key component in managing and maintaining the reliability and stability of web services. Techniques like rate limiting, leaky bucket, token bucket, and exponential backoff have unique strengths, making them suitable for different scenarios. By implementing request throttling, both client-side and server-side, developers can effectively protect their APIs from overuse, abuse, and potential crashes.

By thoughtfully combining these strategies and applying them based on specific use cases, developers can create robust, scalable, and efficient web applications that are resilient under stress.