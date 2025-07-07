import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

BASE_URL = "https://www.mysuncoast.com"
HEADERS = {'User-Agent': 'Mozilla/5.0'}
VISITED = set()

# Fetch the homepage
resp = requests.get(BASE_URL, headers=HEADERS)
soup = BeautifulSoup(resp.content, 'html.parser')

# Initialize RSS feed
fg = FeedGenerator()
fg.title("MySuncoast (ABC7 Sarasota) Custom RSS")
fg.link(href=BASE_URL)
fg.description("Custom feed from mysuncoast.com homepage")
fg.language("en")

# Find and filter article links
article_links = []

for a in soup.find_all("a", href=True):
    href = a["href"]
    if href.startswith("/") and "/202" in href and href not in VISITED:
        full_url = BASE_URL + href
        VISITED.add(href)
        
        try:
            article_page = requests.get(full_url, headers=HEADERS, timeout=5)
            article_soup = BeautifulSoup(article_page.content, "html.parser")

            title = article_soup.find("h1").get_text(strip=True) if article_soup.find("h1") else "Untitled"
            summary_tag = article_soup.find("meta", {"name": "description"}) or article_soup.find("p")
            summary = summary_tag.get("content") if summary_tag and summary_tag.has_attr("content") else summary_tag.get_text(strip=True) if summary_tag else ""

            pub_tag = article_soup.find("meta", {"property": "article:published_time"})
            pub_date = pub_tag["content"] if pub_tag and pub_tag.has_attr("content") else None

            article_links.append((title, full_url, summary, pub_date))
        
        except Exception as e:
            print(f"⚠️ Skipped {full_url}: {e}")

# Add entries to feed
for title, link, summary, pub_date in article_links[:15]:
    fe = fg.add_entry()
    fe.title(title)
    fe.link(href=link)
    fe.description(summary or title)
    if pub_date:
        fe.pubDate(pub_date)

# Output to file
fg.rss_file("mysuncoast.xml")
print("✅ RSS feed generated: mysuncoast.xml")