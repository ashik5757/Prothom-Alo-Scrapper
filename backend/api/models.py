from django.db import models
from django.utils import timezone
from datetime import timedelta



class ScrapingTask(models.Model):

    category = models.CharField(max_length=100, default='bangladesh', unique=True)
    url = models.URLField(max_length=255, blank=True, null=True)
    scheduled_hours = models.PositiveIntegerField(default=1)
    end_time = models.DateTimeField(default=(timezone.now() + timedelta(hours=1)))
    max_contents = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_scraped_at = models.DateTimeField(null=True, blank=True)
    

    def save(self, *args, **kwargs):
        self.url = f"https://www.prothomalo.com/{self.category.strip('/')}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category} - {self.url}"
    

class Content(models.Model):
    scraping_task = models.ForeignKey(ScrapingTask, on_delete=models.CASCADE, related_name='contents')
    url = models.URLField(max_length=255)
    title = models.CharField(max_length=255)
    inner_title = models.TextField(blank=True, null=True)  # Using TextField for longer titles
    author = models.CharField(max_length=200, blank=True, null=True)
    author_location = models.CharField(max_length=200, blank=True, null=True)
    main_story = models.TextField(blank=True, null=True)
    published_time = models.CharField(max_length=100, blank=True, null=True)
    published_time_bn = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
