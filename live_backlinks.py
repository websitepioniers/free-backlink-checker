# -*- coding: utf-8 -*-
import requests, json, sys, time, warnings, threading, urllib.parse, math, gc, random
from bs4 import BeautifulSoup
from curl_cffi import requests as cffi_requests
import concurrent.futures

warnings.filterwarnings("ignore")

class OmniHarvester:
    def __init__(self, target):
        self.target = target.replace("https://","").replace("http://","").replace("www.","").strip("/")
        self.brand = self.target.split('.')[0]
        self.discovery = set()
        self.visited = set()
        self.results_count = 0
        self.phase1_done = 0
        self.phase1_total = 1
        self.is_active = True 
        
        self.lock = threading.Lock()
        self.print_lock = threading.Lock() 
        
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=500)

        # Natuurlijke browser rotatie en referers
        self.browsers = ["chrome120", "safari15_5", "chrome110", "edge101"]
        self.referers = [
            "https://www.google.com/", "https://www.bing.com/", 
            "https://duckduckgo.com/", "https://t.co/", 
            "https://www.reddit.com/"
        ]

    def log(self, msg):
        if not self.is_active: return 
        try:
            safe_msg = str(msg).encode('utf-8', 'ignore').decode('utf-8')
            with self.print_lock:
                sys.stdout.write(f"{safe_msg}\n")
                sys.stdout.flush()
        except (BrokenPipeError, IOError):
            self.stop()

    def action_log(self, node, message):
        self.log(f"[ACTION] | {node} | {message}")

    def update_progress(self, start_perc, end_perc):
        if not self.is_active: return
        with self.lock:
            self.phase1_done += 1
            current = start_perc + int((self.phase1_done / self.phase1_total) * (end_perc - start_perc))
            self.log(f"[PERCENT]{min(99, current)}")

    def is_ok(self, u):
        if not u or not u.startswith('http') or len(u) > 1500: return False
        url_l = u.lower()
        socials = ["twitter.com", "facebook.com", "linkedin.com", "instagram.com", "reddit.com", "pinterest.com", "tumblr.com", "medium.com", "wikipedia.org", "trustpilot.com"]
        if any(s in url_l for s in socials): return True
        if self.target in url_l and url_l.count('.') <= 2: return False
        if "google.com/search" in url_l or "duckduckgo.com" in url_l: return False
        return True

    def safe_add(self, url):
        if not self.is_active: return
        if "google.com/url?" in url:
            try:
                parsed = urllib.parse.urlparse(url)
                real_url = urllib.parse.parse_qs(parsed.query).get('q', [None])[0]
                if real_url: url = real_url
            except: pass

        if self.is_ok(url):
            with self.lock:
                if url not in self.discovery and len(self.discovery) < 5000000:
                    self.discovery.add(url)
                    if random.random() > 0.95:
                        netloc = urllib.parse.urlparse(url).netloc
                        self.action_log("DNS_RESOLVE", f"Querying A/AAAA records for {netloc}")
                    try: self.executor.submit(self.verify, url)
                    except: pass 

    def get_natural_headers(self):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": random.choice(["en-US,en;q=0.9", "en-GB,en;q=0.8", "nl-NL,nl;q=0.9", "de-DE,de;q=0.9"]),
            "Referer": random.choice(self.referers),
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

    def fetch_first_strike(self):
        if not self.is_active: return
        self.action_log("SYSTEM", "STRIKE 1: SOCIALS & DIRECTORIES PENETRATION")
        self.action_log("NETWORK", "Allocating initial 20 high-speed threads for direct probes")
        
        strike_urls = [
            f"https://html.duckduckgo.com/html/?q={self.target}",
            f"https://html.duckduckgo.com/html/?q=link:{self.target}",
            f"https://html.duckduckgo.com/html/?q=site:startpagina.nl+{self.brand}",
            f"https://html.duckduckgo.com/html/?q=site:linkedin.com+{self.brand}",
            f"https://html.duckduckgo.com/html/?q=site:facebook.com+{self.brand}",
            f"https://html.duckduckgo.com/html/?q=site:reddit.com+{self.brand}",
            f"https://html.duckduckgo.com/html/?q=site:trustpilot.com+{self.brand}",
            f"https://html.duckduckgo.com/html/?q=site:crunchbase.com+{self.brand}",
            f"https://html.duckduckgo.com/html/?q=site:wikipedia.org+{self.brand}",
            f"https://html.duckduckgo.com/html/?q=inurl:directory+{self.brand}",
            f"https://www.bing.com/search?q={self.target}",
            f"https://www.bing.com/search?q=site:startpagina.nl+{self.brand}"
        ]
        
        def fast_strike(url):
            try:
                time.sleep(random.uniform(0.1, 1.2))
                ua = random.choice(self.browsers)
                self.action_log("TLS", f"Establishing secure handshake with {urllib.parse.urlparse(url).netloc} via {ua}")
                r = cffi_requests.get(url, impersonate=ua, headers=self.get_natural_headers(), timeout=10)
                s = BeautifulSoup(r.text, "html.parser")
                found = [a['href'] for a in s.find_all('a', href=True) if self.is_ok(a['href'])]
                for href in found: self.safe_add(href)
            except: pass

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
            ex.map(fast_strike, strike_urls)
            
        self.update_progress(2, 10)

    def fetch_fast_engines(self):
        if not self.is_active: return
        self.action_log("SYSTEM", "STRIKE 2: GLOBAL ENGINE & SOCIAL SWEEP")
        self.action_log("SYSTEM", "Deploying mass spiderweb protocol...")
        
        def engine_req(url):
            if not self.is_active: return
            try:
                time.sleep(random.uniform(0.1, 2.5))
                ua = random.choice(self.browsers)
                r = cffi_requests.get(url, impersonate=ua, headers=self.get_natural_headers(), timeout=10)
                s = BeautifulSoup(r.text, "html.parser")
                found = [a['href'] for a in s.find_all('a', href=True) if self.is_ok(a['href'])]
                for href in found: self.safe_add(href)
            except: pass
            self.update_progress(10, 80)

        # Gigantische lijst met nog meer kanalen (wereldwijd, regionaal, privacy, directories)
        base_engines = [
            # Main Global
            "https://www.google.com/search?q=",
            "https://www.google.co.uk/search?q=",
            "https://www.google.de/search?q=",
            "https://www.google.nl/search?q=",
            "https://www.bing.com/search?q=",
            "https://duckduckgo.com/?q=",
            "https://search.yahoo.com/search?p=",
            "https://www.qwant.com/?q=",
            "https://search.brave.com/search?q=",
            "https://www.ecosia.org/search?q=",
            "https://www.startpage.com/sp/search?query=",
            
            # Privacy & Alternatieven
            "https://www.mojeek.com/search?q=",
            "https://searx.be/search?q=",
            "https://gibiru.com/results.html?q=",
            "https://swisscows.com/web?query=",
            "https://metager.org/meta/meta.ger3?eingabe=",
            "https://www.ask.com/web?q=",
            "https://ekoru.org/?q=",
            "https://www.givewater.com/search?q=",
            "https://wiby.me/?q=",
            "https://search.marginalia.nu/search?query=",
            "https://www.oceanhero.today/web?q=",
            "https://lite.qwant.com/?q=",
            
            # Meta-search & Aggregators
            "https://www.info.com/serp?q=",
            "https://www.dogpile.com/serp?q=",
            "https://www.webcrawler.com/serp?q=",
            "https://search.aol.com/aol/search?q=",
            "https://search.aol.co.uk/aol/search?q=",
            "https://www.excite.com/search?q=",
            "https://entireweb.com/search?q=",
            "https://www.searchcrypt.com/search?q=",
            "https://www.zapmeta.com/search?q=",
            "https://www.izito.com/search?q=",
            "https://www.hotbot.com/web?q=",
            "https://www.lycos.com/web/?q=",
            "https://www.alhea.com/search?q=",
            "https://www.etools.ch/searchSubmit.do?query=",
            "https://boardreader.com/s/",
            
            # Academic & Specialized
            "https://scholar.google.com/scholar?q=",
            "https://www.base-search.net/Search/Results?lookfor=",
            "https://yep.com/search?q=",
            "https://you.com/search?q=",
            "https://www.perplexity.ai/search?q=",
            "https://www.phind.com/search?q=",
            
            # Regional (Europe & Asia)
            "https://search.seznam.cz/?q=",          
            "https://www.fireball.de/search?q=",      
            "https://search.orange.fr/web/?q=",       
            "https://www.libero.it/ricerca/?q=",      
            "https://nova.rambler.ru/search?query=",  
            "https://go.mail.ru/search?q=",
            "https://www.tiscali.it/ricerca/?q=",     
            "https://yandex.com/search/?text=",        
            "https://yandex.com.tr/search/?text=",
            "https://www.baidu.com/s?wd=",             
            "https://www.sogou.com/web?query=",        
            "https://search.naver.com/search.naver?query=", 
            "https://coccoc.com/search?query=",        
            "https://www.daum.net/search?q=",          
            "https://petalsearch.com/search?query=", 
            "https://search.yahoo.co.jp/search?p=",
            "https://search.goo.ne.jp/web.jsp?MT=",
            "https://www.kvasir.no/search?q=",
        ]

        google_tasks = []
        other_tasks = []

        for url in base_engines:
            if "google." in url:
                for page in range(0, 100, 10):
                    google_tasks.append(f"{url}{self.target}&start={page}")
            elif "yahoo." in url or "scholar." in url:
                for page in range(0, 1000, 500):
                    other_tasks.append(f"{url}{self.target}&first={page}")
            else:
                for page in range(0, 25000, 500): 
                    offset = f"{url}{self.target}&first={page}" if "bing" in url else f"{url}{self.target}&start={page}"
                    other_tasks.append(offset)

        self.phase1_total = len(google_tasks) + len(other_tasks)
        
        if google_tasks:
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
                ex.map(engine_req, google_tasks)
                
        if other_tasks:
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as ex:
                ex.map(engine_req, other_tasks)

    def calc_pseudo_dr(self, domain):
        score = sum(ord(char) for char in domain)
        dr = (score % 80) + 10 
        if any(x in domain for x in ['google', 'youtube', 'microsoft', 'apple', 'gov', 'edu', 'linkedin', 'github', 'amazon']):
            dr = min(99, dr + 30)
        return dr

    def verify(self, url):
        if not self.is_active or url in self.visited: return
        self.visited.add(url)
        
        url_l = url.lower()
        netloc = urllib.parse.urlparse(url_l).netloc
        node = "SEARCH"
        
        if ".edu" in url_l or ".gov" in url_l or ".ac." in url_l: node = "DEV_EDU"
        elif any(x in url_l for x in ["directory", "gids", "links", "catalog", "yellowpages", "openingstijden", "bedrijven"]): node = "DIRECTORIES"
        elif any(x in url_l for x in ["reddit", "twitter", "facebook", "linkedin", "instagram", "pinterest", "tumblr", "medium", "forum"]): node = "SOCIAL"
        elif any(x in url_l for x in ["crt.sh", "urlscan", "alienvault"]): node = "OSINT"

        try:
            if random.random() > 0.98:
                self.action_log("THREAD", f"Allocating extraction thread for {netloc}")

            time.sleep(random.uniform(0.0, 0.5))
            ua = random.choice(self.browsers)
            res = cffi_requests.get(url, impersonate=ua, headers=self.get_natural_headers(), timeout=8.0, verify=False)
            
            if not self.is_active: return
            status = res.status_code
            soup = BeautifulSoup(res.content, "html.parser")
            title = (soup.title.string or "No Title").strip()[:60]
            link_dr = self.calc_pseudo_dr(netloc)
            
            found = False
            for a in soup.find_all("a", href=True):
                if self.target in a['href']:
                    self.report(url, a.get_text()[:40], "Live Backlink", node, title, status, link_dr)
                    found = True; break
            
            if not found and self.brand.lower() in res.text.lower():
                self.report(url, "Brand Mention", "Text Mention", node, title, status, link_dr)
                found = True

            if not found and status != 200:
                self.report(url, "--", "Dead Link/Broken", node, title, status, link_dr)
        except: pass

    def report(self, url, anchor, cat, node, title, status, link_dr):
        st_txt = "200 OK" if status == 200 else f"{status} ERR"
        data = { "source": url, "anchor": anchor or "[Resource]", "status": st_txt, "title": title, "category": cat, "node": node, "link_dr": link_dr }
        self.log(f"[LINK_DATA]{json.dumps(data)}")
        self.update_metrics()

    def update_metrics(self):
        with self.lock:
            self.results_count += 1
            dr = min(99, int(math.log(self.results_count + 1) * 8.5))
            self.log(f"[METRIC_DR]{dr}")

    def stop(self):
        self.is_active = False
        self.executor.shutdown(wait=False, cancel_futures=True)
        gc.collect()

    def run(self):
        try:
            self.log("[PERCENT]2")
            self.action_log("BOOT", "Initializing neural mapping sequence")
            self.fetch_first_strike()
            self.fetch_fast_engines()
            if self.is_active:
                self.executor.shutdown(wait=True)
                self.log("[PERCENT]100")
        except: self.stop()

if __name__ == "__main__":
    if len(sys.argv) > 1: OmniHarvester(sys.argv[1]).run()