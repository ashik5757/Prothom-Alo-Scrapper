# news/serializers.py
from rest_framework import serializers
from .models import ScrapingTask, Content

class ScrapingTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapingTask
        fields = "__all__"
        read_only_fields = ['url','created_at', 'updated_at', 'last_scraped_at']

        def get_content_count(self, obj):
            return obj.contents.count()


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = "__all__"
        read_only_fields = ['scraping_task', 'created_at']