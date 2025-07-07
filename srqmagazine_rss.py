import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

BASE_URL = "https://www.srqmagazine.com"
HEADERS = {'User-Agent': 'Mozilla/5.0'}
VISITED = set()

# Fetch homepage
resp = requests.get(BASE_URL, headers=HEADERS)
soup = BeautifulSoup(resp.content, "html.parser")

# Setup feed
fg = FeedGenerator()
fg.title("SRQ Magazine Custom RSS")
fg.link(href=BASE_URL)
fg.description("Custom RSS feed for SRQ Magazine")
fg.language("en")

# Gather article links
article_links = []

for a in soup.find_all("a", href=True):
    href = a["href"]
    if href.startswith("/") and "articles" in href and href not in VISITED:
        full_url = BASE_URL + href
        VISITED.add(href)

        try:
            article_resp = requests.get(full_url, headers=HEADERS, timeout=5)
            article_soup = BeautifulSoup(article_resp.content, "html.parser")

            # Title
            title = article_soup.find("h1").get_text(strip=True) if article_soup.find("h1") else "Untitled"

            # Summary
            summary_tag = article_soup.find("p")
            summary = summary_tag.get_text(strip=True) if summary_tag else ""

            # Publish date (if any metadata available)
            pub_tag = article_soup.find("meta", {"name": "date"})
            pub_date = pub_tag["content"] if pub_tag and pub_tag.has_attr("content") else None

            article_links.append((title, full_url, summary, pub_date))

        except Exception as e:
            print(f"⚠️ Skipped {full_url}: {e}")

# Add items to feed
for title, url, summary, pub_date in article_links[:15]:
    fe = fg.add_entry()
    fe.title(title)
    fe.link(href=url)
    fe.description(summary or title)
    if pub_date:
        fe.pubDate(pub_date)

# Output RSS XML
fg.rss_file("srqmagazine.xml")
print("✅ RSS feed generated: srqmagazine.xml")