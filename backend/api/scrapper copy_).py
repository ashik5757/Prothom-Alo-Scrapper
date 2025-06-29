import requests
from bs4 import BeautifulSoup
import logging
import time
import random
from django.utils import timezone
from .models import Content
from .es_client import es, INDEX_NAME

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_es_index_if_not_exists():
    """Create Elasticsearch index with appropriate mapping if it doesn't exist"""
    try:
        if not es.indices.exists(index=INDEX_NAME):
            # Define mappings for better search capabilities
            index_settings = {
                "mappings": {
                    "properties": {
                        "title": {"type": "text", "analyzer": "standard"},
                        "description": {"type": "text", "analyzer": "standard"},
                        "url": {"type": "keyword"},
                        "category": {"type": "keyword"},
                        "timestamp": {"type": "date"}
                    }
                }
            }
            
            # Use the correct parameter name for Elasticsearch 8.x
            es.indices.create(
                index=INDEX_NAME,
                settings=index_settings
            )
            logger.info(f"Created Elasticsearch index: {INDEX_NAME}")
    except Exception as e:
        logger.error(f"Error creating Elasticsearch index: {e}")


def index_to_elasticsearch(content):
    """Index a Content object to Elasticsearch"""
    try:
        # Prepare document for indexing
        document = {
            "title": content.title,
            "description": content.description or "",
            "url": content.url,
            "category": content.scraping_task.category,
            "timestamp": content.created_at.isoformat(),
        }
        
        # Index document
        es.index(
            index=INDEX_NAME,
            document=document,
            id=str(content.id),
        )
        logger.info(f"Indexed content '{content.title}' to Elasticsearch with ID {content.id}")
    except Exception as e:
        logger.error(f"Error indexing to Elasticsearch: {e}")

# def get_article_description(url):
#     """Fetch and extract description for an article URL"""
#     try:
#         # Add a delay to avoid hammering the server
#         time.sleep(random.uniform(1, 2))
        
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#         }
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()
        
#         soup = BeautifulSoup(response.content, 'html.parser')
        
#         # Try to get description from meta tags
#         description = ""
#         description_el = soup.find('meta', property='og:description')
#         if description_el and description_el.get('content'):
#             description = description_el.get('content')
        
#         # If meta description not found, look for first paragraph
#         if not description:
#             first_para = soup.find('p')
#             if first_para:
#                 description = first_para.text.strip()
                
#         return description
#     except Exception as e:
#         logger.error(f"Error getting description from {url}: {e}")
#         return ""



def scrape_and_store(task):
    """
    Scrape content from Prothom Alo website based on task parameters
    and store in both database and Elasticsearch.
    """
    logger.info(f"Starting scraping task for URL: {task.url}")
    
    # Ensure Elasticsearch index exists
    create_es_index_if_not_exists()
    
    # Define base URL and category
    base_url = "https://www.prothomalo.com"
    category = task.category.strip('/')
    category_url_prefix = f"{base_url}/{category}"
    
    logger.info(f"Using category prefix: {category_url_prefix}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(task.url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching URL {task.url}: {e}")
        return
    
    # Parse HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Get all links from the page
    all_links = soup.find_all('a', href=True)
    logger.info(f"Found {len(all_links)} total links on the page")
    
    # Filter links based on category
    category_links = []
    for link in all_links:
        href = link.get('href', '')
        
        # Convert relative URLs to absolute
        if href.startswith('/'):
            href = f"{base_url}{href}"
        
        # Only include links that start with the category URL prefix
        if href.startswith(category_url_prefix):
            category_links.append(link)
    
    logger.info(f"Filtered down to {len(category_links)} links matching category '{category}'")
    
    count = 0
    for link in category_links:
        if count >= task.max_contents:
            break
            
        # Get URL from href attribute
        url = link.get('href')
        
        # Convert relative URLs to absolute
        if url.startswith('/'):
            url = f"{base_url}{url}"
        
        # Find title - first try span with class="tilte-no-link-parent"
        title_span = link.find('span', class_='tilte-no-link-parent')
        
        if title_span:
            title = title_span.text.strip()
        else:
            # If specific span not found, try to extract text directly
            title = link.get_text().strip()
            
        if not title or len(title) < 5:
            continue
            
        # Skip if content already exists
        if Content.objects.filter(url=url, scraping_task=task).exists():
            logger.debug(f"Content with URL {url} already exists, skipping")
            continue
        
        logger.info(f"Found article: {title[:50]}... at {url}")
        
        # Create new Content object in database
        content = Content.objects.create(
            scraping_task=task,
            title=title,
            description="",  # No description as per requirement
            url=url
        )
        
        # Index in Elasticsearch
        index_to_elasticsearch(content)
        
        count += 1
        
        # Add a small delay between processing articles
        time.sleep(random.uniform(0.2, 0.5))
    
    # Update the last scraped time
    task.last_scraped_at = timezone.now()
    task.save()
    
    logger.info(f"Completed scraping task, processed {count} articles")








