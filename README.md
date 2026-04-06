# OmniHarvester 🕷️🌍
**The Ultimate Free Open-Source Backlink Checker & OSINT Spider**

OmniHarvester is a hyper-threaded, hyper-scalable backlink discovery tool. It bypasses commercial search engine limits, CAPTCHAs, and firewalls by combining stealth browser spoofing, API connections, and a massive global engine matrix. It doesn't just scrape; it interrogates the entire internet for mentions of your domain.

![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Maintained](https://img.shields.io/badge/maintained-yes-brightgreen.svg)

## 🚀 Live Demo
*Try the tool live without installing anything!*
👉 [**[Link to your Live Demo here - e.g., hosted on Streamlit/Vercel]**](https://sumenos.com/seo/)

## 🔥 Key Features
* **Hyper-Threaded Architecture:** Runs up to 250 asynchronous network requests and 1000 parsing threads simultaneously. Built for raw speed and deep memory management (`gc.collect()`).
* **DuckDuckGo POST Matrix:** Bypasses limits by firing hidden POST requests with alphanumeric matrix queries (a-z, 0-9) directly to DuckDuckGo's HTML endpoints.
* **Global Infrastructure Bypass:** Employs the new Google `&udm=14` and `&filter=0` retro-hack, and Bing `&cc=` country-code scoping to force search engines to drop heavy JS and CAPTCHA walls.
* **30+ Search Engines Worldwide:** Scans globally across Brave, Yandex, Yahoo, Ecosia, Qwant, Mojeek, Boardreader, Baidu, Naver, and dozens of local engines using their exact pagination rules.
* **100% Block-Free OSINT APIs:** Connects directly to the Wayback Machine (Internet Archive), AlienVault OTX, URLScan, HackerNews, and Crossref Academic databases.
* **Automated Auto-Discovery:** Dynamically finds global web directories, B2B portals, and startpages to search within them.
* **Deep Regex Siphoning:** Extracts hidden JSON and Javascript links that standard HTML parsers (`BeautifulSoup`) miss.
   ```bash
   git clone [https://github.com/yourusername/OmniHarvester.git](https://github.com/yourusername/OmniHarvester.git)
   cd OmniHarvester
