from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from .models import ScrapingTask, Content
import time
from datetime import datetime, timedelta
from api.schedule import update_task_schedule
from .models import ScrapingTask, Content
from .es_client import es, INDEX_NAME
from celery import shared_task
from django.utils import timezone

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


@shared_task
def scrape_and_store(scraping_task_id):

    try:
        scraping_task = ScrapingTask.objects.get(id=scraping_task_id)
        
        if not scraping_task.is_active:
            print(f"Task {scraping_task_id} is inactive. Skipping execution.")
            return
        
        
        ## For Local environment : =======================

        # options = Options()
        # options.add_argument("--headless")
        # options.add_argument("--disable-gpu")
        # options.add_argument("--no-sandbox")
        # options.add_argument("user-agent=Mozilla/5.0")
        # driver = webdriver.Chrome(options=options)





        ## For Docker environment : =======================

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("user-agent=Mozilla/5.0")

        # Set the binary location to Chromium (inside Debian/Ubuntu-based Docker)
        options.binary_location = "/usr/bin/chromium"

        # Optional: explicitly point to chromedriver path (usually not needed if installed via apt)
        # service = Service("/usr/lib/chromium/chromedriver")

        # Create driver
        driver = webdriver.Chrome(options=options)





        url = scraping_task.url
        driver.get(url)
        
        
        print("Starting to scroll page to load all content...")
        scroll_pause_time = 1.5
        screen_height = driver.execute_script("return window.screen.height;")
        i = 1
        
        while True:
            # Scroll one screen height each time
            driver.execute_script(f"window.scrollTo(0, {screen_height * i});")
            i += 1
            time.sleep(scroll_pause_time)
            
            # Calculate scroll height after scroll
            scroll_height = driver.execute_script("return document.body.scrollHeight;")
            current_position = driver.execute_script("return window.pageYOffset;")
            visible_height = driver.execute_script("return window.innerHeight;")
            # Break if we've scrolled to the bottom or after 30 scrolls
            if (current_position + visible_height) >= scroll_height or i > 30:
                print(f"Reached end of page or maximum scrolls ({i-1} scrolls)")
                break
                
        # Additional wait after scrolling to ensure everything loaded
        time.sleep(3)


        load_more_attempts = 0
        max_load_more_clicks = scraping_task.max_contents // 10  


        try:
            while load_more_attempts < max_load_more_clicks:
                try:
                    load_more_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'more') and contains(@class, '_7ZpjE')]"))
                    )

                    driver.execute_script("arguments[0].click();", load_more_button)
                    load_more_attempts += 1

                    time.sleep(3) 

                except TimeoutException:
                    print("Timeout while waiting for load more button. Stopping attempts.")
                    break
                except NoSuchElementException:
                    print("Load more button not found. Stopping attempts.")
                    break
            
            print(f"Completed {load_more_attempts} attempts to load more articles.")
        
        except Exception as e:
            print(f"Error during load more attempts: {e}")
            

        html = driver.page_source
        # driver.quit()

        soup = BeautifulSoup(html, "html.parser")

        articles = []
        seen_urls = set()

        # --- Updated selector: get from aria-label and href ---
        for a in soup.select("a[aria-label][href]"):
            title = a.get("aria-label")
            href = a.get("href")

            if title and href and "/"+ scraping_task.category +"/" in href:
                full_url = href if href.startswith("http") else "https://www.prothomalo.com" + href
                if full_url not in seen_urls:
                    articles.append({
                        "title": title,
                        "url": full_url,
                        "category": scraping_task.category
                    })
                    seen_urls.add(full_url)

        # Try another selector for additional articles
        for article in soup.select("div.bn-story-card"):
            link_element = article.select_one("a.link-overlay")
            title_element = article.select_one("h2.headline") or article.select_one("span.title-text")
            
            if link_element and title_element:
                href = link_element.get("href")
                title = title_element.get_text(strip=True)
                
                if href and title and "/"+ scraping_task.category +"/" in href:
                    full_url = href if href.startswith("http") else "https://www.prothomalo.com" + href
                    if full_url not in seen_urls:
                        articles.append({
                            "title": title,
                            "url": full_url,
                            "category": scraping_task.category
                        })
                        seen_urls.add(full_url)

        def scrap_content_details(article_url):
            try:
                print(f"Scraping content details for {article_url}")
                driver.get(article_url)
                time.sleep(2)

                article_data = {}

                try:
                    title_element = driver.find_element(By.CSS_SELECTOR, "h1[data-title-0]")
                    article_data["inner_title"] = title_element.text
                except (NoSuchElementException, TimeoutException):
                    article_data["inner_title"] = ""

                try:
                    author_element = driver.find_element(By.CSS_SELECTOR, "span.contributor-name._8TSJC")
                    article_data["author"] = author_element.text
                except (NoSuchElementException, TimeoutException):
                    article_data["author"] = ""
                
                try:
                    location_element = driver.find_element(By.CSS_SELECTOR, "span.author-location._8-umj")
                    article_data["author_location"] = location_element.text
                except (NoSuchElementException, TimeoutException):
                    article_data["author_location"] = ""

                try:
                    time_element = driver.find_element(By.CSS_SELECTOR, "time span")
                    article_data["published_time_bn"] = time_element.text

                    parent_time = driver.find_element(By.CSS_SELECTOR, "time")
                    datetime_value = parent_time.get_attribute("datetime")
                    
                    if datetime_value and datetime_value.strip():
                        article_data["published_time"] = datetime_value

                    # datetime_str = parent_time.get_attribute("datetime")

                    # if datetime_str and isinstance(datetime_str, str):
                    #     # Convert to datetime object
                    #     dt = datetime.fromisoformat(datetime_str)
                    #     article_data["published_time"] = dt.strftime("%Y-%m-%dT%H:%M:%S%z")



                except (NoSuchElementException, TimeoutException):
                    article_data["published_time_bn"] = ""
                    # article_data["published_time"] = ""

                main_story = ""
                try:
                    story_elements = driver.find_elements(By.CSS_SELECTOR, "div.story-element.story-element-text p")            
                    for element in story_elements:
                        main_story += element.text + "\n"
                except (NoSuchElementException, TimeoutException):
                    pass

                article_data["main_story"] = main_story.strip()
                return article_data
            
            except Exception as e:
                print(f"Error scraping content details for {article_url}: {e}")
                return {}
            



            

        content_created = 0
        for article in articles:
            
            print(f"Processing article: {article['title']} ({article['url']})")
            article_details = scrap_content_details(article["url"])
            article.update(article_details)

            # print(f"Article data being indexed: {article.keys()}")
            es.index(index=INDEX_NAME, id=article["url"], document=article)
            scraping_task.last_scraped_at = timezone.now().isoformat()
            scraping_task.save(update_fields=['last_scraped_at'])

            
            try:
                obj, created = Content.objects.get_or_create(
                    scraping_task=scraping_task,
                    url=article["url"],
                    defaults={
                        "title": article["title"],
                        "inner_title": article.get("inner_title", ""),
                        "author": article.get("author", ""),
                        "author_location": article.get("author_location", ""),
                        "published_time": article.get("published_time", ""),
                        "published_time_bn": article.get("published_time_bn", ""),
                        "main_story": article.get("main_story", "")
                    }
                )
                if created:
                    content_created += 1
            except Exception as e:
                print(f"Error creating content: {e}")

        
        driver.quit()



        scraping_task.last_scraped_at = timezone.now().isoformat()

        current_content_count = Content.objects.filter(scraping_task=scraping_task_id).count()
        print(f"Current content count for task {scraping_task_id}: {current_content_count}")

        updated_content_count = current_content_count + content_created
        if updated_content_count >= scraping_task.max_contents:
            print(f"Task {scraping_task_id} has now crossed max_contents ({scraping_task.max_contents}). Disabling task.")
            scraping_task.is_active = False
            scraping_task.save(update_fields=['is_active', 'last_scraped_at'])
            update_task_schedule(scraping_task_id, False)
        else:
            scraping_task.save(update_fields=['last_scraped_at'])

        print(f"✅ Indexed {len(articles)} articles into Elasticsearch, created {content_created} new Content objects.")

    except ScrapingTask.DoesNotExist:
        print(f"❌ Scraping task with ID {scraping_task_id} does not exist.")
    except Exception as e:
        print(f"❌ An error occurred while scraping: {e}")
        if 'driver' in locals():
            driver.quit()

