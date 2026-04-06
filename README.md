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
🖥️ Installation via SSH (VPS / Dedicated Linux Server)
Because this scraper can run for 1 to 2 hours depending on the queue size, running it on a remote server via SSH is highly recommended. We will use screen so the process continues running even if your SSH connection drops.

Step 1: Connect to your server

Bash
ssh username@your_server_ip
Step 2: Update packages and install dependencies

Bash
sudo apt update && sudo apt upgrade -y
sudo apt install git python3 python3-pip python3-venv screen -y
Step 3: Clone the repository

Bash
git clone [https://github.com/yourusername/OmniHarvester.git](https://github.com/yourusername/OmniHarvester.git)
cd OmniHarvester
Step 4: Create and activate a Virtual Environment

Bash
python3 -m venv venv
source venv/bin/activate
Step 5: Install Python requirements

Bash
pip install -r requirements.txt
Step 6: Run OmniHarvester in the background using screen
Start a new virtual terminal session:

Bash
screen -S scraper
Run the tool:

Bash
python live_backlinks.py yourwebsite.com
To safely detach from the screen and leave it running in the background, press: CTRL + A, then press D.
To reattach and check the progress later, type: screen -r scraper.

🔑 Premium APIs (Optional but Recommended)
To get 100% guaranteed, block-free results from Google and Bing, you can add your official API keys at the top of the live_backlinks.py file:

Python
self.api_keys = {
    "google_api_key": "YOUR_API_KEY", 
    "google_cx_id": "YOUR_CX_ID",   
    "bing_api_key": "YOUR_BING_KEY"    
}
If left empty, the tool will automatically fall back to its aggressive proxy-swarm scraping method.
