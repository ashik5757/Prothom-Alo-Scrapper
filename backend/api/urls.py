
from django.urls import path

from api.views import ScrapingTaskListCreate, ScrapingTaskDetail, ScrapingTaskContentList, ContentListCreate, ScrappingTaskElasticSearchList, GenericElasticSearchList


urlpatterns = [
    path('tasks/', ScrapingTaskListCreate.as_view(), name='scraping-task-list-create'),
    path('tasks/<int:pk>/', ScrapingTaskDetail.as_view(), name='scraping-task-detail'),

    path('tasks/<int:pk>/contents/', ScrapingTaskContentList.as_view(), name='scraping-task-contents'),
    path('tasks/<int:pk>/elastic-search/', ScrappingTaskElasticSearchList.as_view(), name='scraping-task-elastic-search'),

    path('tasks/elastic-search/', GenericElasticSearchList.as_view(), name='generic-elastic-search'),

    path('contents/', ContentListCreate.as_view(), name='content-list-create'), 
]
