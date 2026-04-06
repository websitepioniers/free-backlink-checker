from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import json
import sys
import time
import random
import os
import requests # Gebruik de super-stabiele standaard library

class DeepCrawler:
    def __init__(self, start_url, max_pages=50):
        self.start_url = start_url
        self.domain = urlparse(start_url).netloc
        self.max_pages = max_pages
        
        self.visited_urls = set()
        self.urls_to_visit = [start_url] 
        
        self.site_data = {
            "domain": self.domain,
            "crawled_pages": [],
            "global_external_links": []
        }
        
        self.referers = [
            "https://www.google.com/", "https://www.bing.com/", 
            f"https://{self.domain}/" 
        ]

        self.kb_file = "omni_knowledge_base.json"
        self.kb = {"dead_links": [], "domains": {}, "tld_stats": {}}
        self.load_kb()

    def load_kb(self):
        if os.path.exists(self.kb_file):
            try:
                with open(self.kb_file, 'r') as f:
                    data = json.load(f)
                    self.kb.update(data)
            except: pass

    def save_kb(self):
        try:
            with open(self.kb_file, 'w') as f:
                json.dump(self.kb, f, indent=4)
        except: pass

    def get_natural_headers(self):
        return {
            "User-Agent": random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15"
            ]),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": random.choice(["en-US,en;q=0.9", "en-GB,en;q=0.8"]),
            "Referer": random.choice(self.referers),
            "Connection": "keep-alive"
        }

    # --- AI ML SCORING ---
    def ai_score_url(self, url):
        """Voorspelt ROI van de URL obv opgebouwde Knowledge Base statistieken"""
        score = 0
        url_lower = url.lower()
        parsed = urlparse(url_lower)
        tld = parsed.netloc.split('.')[-1]
        
        if tld in self.kb.get("tld_stats", {}):
            stats = self.kb["tld_stats"][tld]
            if stats["attempts"] > 5:
                conversion = stats["success"] / stats["attempts"]
                if conversion > 0.1: score += 30 

        gold_words = ["blog", "partner", "link", "sponsor", "over", "about", "contact"]
        if any(word in url_lower for word in gold_words): score += 20
            
        junk_words = ["tag", "category", "author", "page", "login", "cart", "wp-admin"]
        if any(word in url_lower for word in junk_words): score -= 50
            
        return score

    def crawl(self):
        print(f"=== Start AI-Assisted Deep Crawl voor {self.domain} ===")
        print(f"[*] Limiet ingesteld op maximaal {self.max_pages} pagina's.")
        print(f"[*] AI Prediction Matrix: ACTIEF\n")
        
        while self.urls_to_visit and len(self.visited_urls) < self.max_pages:
            self.urls_to_visit.sort(key=lambda u: self.ai_score_url(u), reverse=True)
            current_url = self.urls_to_visit.pop(0)
            
            if current_url in self.visited_urls: continue

            if current_url in self.kb.get("dead_links", []):
                print(f"  [AI-SKIP] Bekende dode link geëlimineerd: {current_url}")
                self.visited_urls.add(current_url)
                continue
                
            print(f"[{len(self.visited_urls) + 1}/{self.max_pages}] Analyseren: {current_url} (AI Predictie: {self.ai_score_url(current_url)})")
            
            try:
                headers = self.get_natural_headers()
                
                # Standaard Requests + Timeout om vastlopen te voorkomen
                response = requests.get(current_url, headers=headers, timeout=10, verify=False)
                self.visited_urls.add(current_url)
                
                if response.status_code in [404, 403, 410, 500, 502, 503]:
                    if "dead_links" not in self.kb: self.kb["dead_links"] = []
                    if current_url not in self.kb["dead_links"]: self.kb["dead_links"].append(current_url)

                page_info = {
                    "url": current_url, "status_code": response.status_code,
                    "title": None, "internal_links_found": 0, "external_links_found": 0
                }
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "html.parser")
                    if soup.title and soup.title.string: page_info["title"] = soup.title.string.strip()
                        
                    for a_tag in soup.find_all("a"):
                        href = a_tag.attrs.get("href")
                        if not href: continue
                            
                        href = urljoin(current_url, href).split('#')[0] 
                        parsed_href = urlparse(href)
                        
                        if not parsed_href.scheme in ['http', 'https']: continue
                            
                        if parsed_href.netloc == self.domain:
                            page_info["internal_links_found"] += 1
                            if href not in self.visited_urls and href not in self.urls_to_visit:
                                self.urls_to_visit.append(href)
                        else:
                            page_info["external_links_found"] += 1
                            link_data = {"from_page": current_url, "to_url": href, "anchor_text": a_tag.text.strip().replace('\n', ' ')}
                            if link_data not in self.site_data["global_external_links"]:
                                self.site_data["global_external_links"].append(link_data)
                                
                self.site_data["crawled_pages"].append(page_info)
                time.sleep(random.uniform(0.5, 2.0))
                
            except requests.exceptions.Timeout:
                print(f"  [!] Fout: Connection Timed Out bij {current_url}")
                self.visited_urls.add(current_url)
            except Exception as e:
                print(f"  [!] Fout bij {current_url}: {e}")
                self.visited_urls.add(current_url)
                if "dead_links" not in self.kb: self.kb["dead_links"] = []
                if current_url not in self.kb["dead_links"]: self.kb["dead_links"].append(current_url)
                
        self.save_data()
        self.save_kb() 

    def save_data(self):
        filename = f"deepcrawl_{self.domain.replace('.', '_')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.site_data, f, ensure_ascii=False, indent=4)
            
        print(f"\n[V] Deep Crawl voltooid! Data en geüpdatet brein opgeslagen in: {filename}")

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    if len(sys.argv) < 2:
        print("Gebruik: python3 bot.py https://voorbeeld.nl")
        sys.exit()
    DeepCrawler(sys.argv[1], max_pages=50).crawl()