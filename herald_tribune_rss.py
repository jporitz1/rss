import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

# Define target
URL = "https://www.heraldtribune.com/"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

# Fetch the homepage
response = requests.get(URL, headers=HEADERS)
soup = BeautifulSoup(response.content, 'html.parser')

# Feed setup
fg = FeedGenerator()
fg.title('Herald-Tribune Custom Feed')
fg.link(href=URL)
fg.description('Latest headlines from the Sarasota Herald-Tribune')

# Extract article blocks
articles = soup.select('a.gnt_m_th_a')  # These are main headline links

# Limit to 10 articles
for link in articles[:10]:
    title = link.get_text(strip=True)
    href = link.get('href')
    if not href.startswith('http'):
        href = "https://www.heraldtribune.com" + href

    entry = fg.add_entry()
    entry.title(title)
    entry.link(href=href)
    entry.description(title)

# Output RSS XML
fg.rss_file('heraldtribune.xml')
print("RSS feed generated: heraldtribune.xml")