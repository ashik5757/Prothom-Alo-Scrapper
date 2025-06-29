# news/scraper.py
import requests
from bs4 import BeautifulSoup
from .models import Content
from .es_client import es, INDEX_NAME
from .models import ScrapingTask
from django.utils import timezone


def scrape_and_store(task):
    """Scrape articles for a specific task and store to DB & Elasticsearch."""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(task.url, headers=headers)

    if response.status_code != 200:
        return f"Failed to fetch from {task.url}"

    soup = BeautifulSoup(response.text, "html.parser")
    articles = []
    seen_urls = set(Content.objects.filter(scraping_task=task).values_list("url", flat=True))

    for tag in soup.select("div.card-wrapper a[href]"):
        full_url = "https://www.prothomalo.com" + tag["href"]
        title = tag.get_text(strip=True)

        if full_url in seen_urls:
            continue

        content = Content.objects.create(
            scraping_task=task,
            title=title,
            url=full_url,
        )

        # Index to Elasticsearch
        es.index(index=INDEX_NAME, id=str(content.id), document={
            "title": content.title,
            "url": content.url,
            "category": task.category,
            "task_id": task.id,
        })

        articles.append(content)

        if len(articles) >= task.max_contents:
            break

    # Update task metadata
    task.last_scraped_at = timezone.now()
    task.save()

    return f"Scraped and stored {len(articles)} new articles."
