import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

BASE_URL = "https://www.heraldtribune.com"
HEADERS = {'User-Agent': 'Mozilla/5.0'}
VISITED = set()

# Fetch homepage
response = requests.get(BASE_URL, headers=HEADERS)
soup = BeautifulSoup(response.content, 'html.parser')

# Setup RSS feed
fg = FeedGenerator()
fg.title('Herald-Tribune (Custom RSS - Broad Article Grab)')
fg.link(href=BASE_URL)
fg.description('A personal RSS feed with broader article scraping from heraldtribune.com')
fg.language('en')

# Extract article links
article_links = []

for link in soup.find_all("a", href=True):
    href = link["href"]

    if href.startswith("/"):
        href = BASE_URL + href

    if (
        "heraldtribune.com/story" in href and
        "classifieds" not in href and
        href not in VISITED
    ):
        VISITED.add(href)
        try:
            article_resp = requests.get(href, headers=HEADERS, timeout=5)
            article_soup = BeautifulSoup(article_resp.content, 'html.parser')

            # Summary
            summary_tag = article_soup.find('p')
            summary = summary_tag.get_text(strip=True) if summary_tag else ""

            # Publish date
            pub_date_tag = article_soup.find('meta', attrs={'name': 'article:published_time'}) or article_soup.find('time')
            pub_date = pub_date_tag['content'] if pub_date_tag and pub_date_tag.has_attr('content') else None

            article_links.append((link.get_text(strip=True), href, summary, pub_date))

        except Exception as e:
            print(f"Error fetching {href}: {e}")

# Add entries to feed
for title, url, summary, pub_date in article_links[:15]:
    fe = fg.add_entry()
    fe.title(title or "Untitled")
    fe.link(href=url)
    fe.description(summary or title or url)
    if pub_date:
        fe.pubDate(pub_date)

# Save RSS XML
fg.rss_file('heraldtribune.xml')
print("✅ RSS feed regenerated: heraldtribune.xml")