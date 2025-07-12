---
source: web_stealth_http
type: stealth_scraping
date: 2025-07-08
url: https://www.morningstar.com/stocks/xnas/aapl/quote
final_url: https://www.morningstar.com/stocks/xnas/aapl/quote
title: ""
status: detection_warning
status_code: 202
bot_detected: True
content_length: 450
html_length: 2429
stealth_method: stealth-requests
content_hash: 4de8adb628da3024
timestamp: 2025-07-08T07:15:05.079742
---

# 

**URL:** https://www.morningstar.com/stocks/xnas/aapl/quote  
**Final URL:** https://www.morningstar.com/stocks/xnas/aapl/quote  
**Status:** detection_warning (HTTP 202)  
**Bot Detection:** ⚠️ WARNING  
**Content Length:** 450 characters  
**Stealth Method:** stealth-requests  
**Scraped:** 2025-07-08T07:15:05.079742  

## Main Content

AwsWafIntegration.saveReferrer(); AwsWafIntegration.checkForceRefresh().then((forceRefresh) => { if (forceRefresh) { AwsWafIntegration.forceRefreshToken().then(() => { window.location.reload(true); }); } else { AwsWafIntegration.getToken().then(() => { window.location.reload(true); }); } }); JavaScript is disabled In order to continue, we need to verify that you're not a robot. This requires JavaScript. Enable JavaScript and then reload the page.







## Response Headers

```json
access-control-allow-headers: x-amzn-waf-action
access-control-allow-methods: OPTIONS,GET,POST
access-control-allow-origin: '*'
access-control-max-age: '86400'
alt-svc: h3=":443"; ma=86400
cache-control: no-store, max-age=0
content-length: '2429'
content-type: text/html; charset=UTF-8
date: Tue, 08 Jul 2025 01:45:05 GMT
server: CloudFront
via: 1.1 4cdd12b2f327a132d9c060a2a8a76b36.cloudfront.net (CloudFront)
x-amz-cf-id: 5nTEeX4v3Nk0g0AcpuSNSenRHpslMMKmP7eK0Qd1aVKeqKFRiqHDNw==
x-amz-cf-pop: HYD57-P2
x-amzn-waf-action: challenge
x-cache: Error from cloudfront

```

## Tags

#web_scraping #stealth #http_only #bot_detected #stealth_requests

---
*Scraped via HTTP stealth framework on 2025-07-08 07:15:05*
