import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import csv
import time

# ============== CONFIG ==============
DOMAINS = [
    "examle","example"
]
MAX_URLS = 100
OUTPUT_CSV = "seo_scraping_output_nuevos.csv"

# ========== FUNCIONES ==========

def get_internal_urls(domain, limit=100):
    seen = set()
    to_visit = [domain]
    internal_urls = []

    while to_visit and len(internal_urls) < limit:
        url = to_visit.pop(0)
        if url in seen or urlparse(url).netloc != urlparse(domain).netloc:
            continue
        seen.add(url)
        try:
            response = requests.get(url, timeout=5)
            if 'text/html' not in response.headers.get('Content-Type', ''):
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            internal_urls.append(url)
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                if urlparse(full_url).netloc == urlparse(domain).netloc:
                    to_visit.append(full_url)
        except Exception:
            continue
    return internal_urls[:limit]

def scrape_url_data(domain, url):
    try:
        start = time.time()
        r = requests.get(url, timeout=10)
        ttfb = r.elapsed.total_seconds()
        page_size_kb = len(r.content) / 1024
        soup = BeautifulSoup(r.text, 'html.parser')

        status = r.status_code
        title = soup.title.string.strip() if soup.title else ''
        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc['content'].strip() if meta_desc else ''
        h1s = "; ".join(h.get_text(strip=True) for h in soup.find_all('h1'))
        h2s = "; ".join(h.get_text(strip=True) for h in soup.find_all('h2'))
        schema = "Yes" if soup.find_all(attrs={"type": "application/ld+json"}) else "No"
        canonical_tag = soup.find("link", rel="canonical")
        canonical = canonical_tag['href'].strip() if canonical_tag else ''
        meta_robots = soup.find("meta", attrs={"name": "robots"})
        robots = meta_robots['content'].strip() if meta_robots else ''

        # Enlaces rotos internos
        broken = 0
        for a in soup.find_all('a', href=True):
            link = urljoin(url, a['href'])
            try:
                if urlparse(link).netloc == urlparse(url).netloc:
                    res = requests.head(link, timeout=5)
                    if res.status_code >= 400:
                        broken += 1
            except:
                broken += 1

        print(f"[{domain}] {url}")
        print(f"  → Status: {status}, TTFB: {round(ttfb, 2)}s, BrokenLinks: {broken}")
        print(f"  → Title: {title[:60]}{'...' if len(title) > 60 else ''}\n")

        return [domain, url, status, title, description, h1s, h2s, schema, canonical, robots, round(ttfb, 2), round(page_size_kb, 1), broken]
    except Exception as e:
        print(f"[ERROR] {url} → {e}\n")
        return [domain, url, 'Error', '', '', '', '', '', '', '', '', '', '']

# ========== EJECUCIÓN ==========

with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Dominio', 'URL', 'Status', 'Title', 'Description', 'H1', 'H2', 'Schema', 'Canonical', 'Meta Robots', 'TTFB', 'PageSize(KB)', 'BrokenLinks'])

    for domain in DOMAINS:
        print(f"\n🌐 Procesando dominio: {domain}")
        urls = get_internal_urls(domain, MAX_URLS)
        for url in urls:
            data = scrape_url_data(domain, url)
            writer.writerow(data)

print(f"\n✅ Scraping finalizado. Archivo generado: {OUTPUT_CSV}")
