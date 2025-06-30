from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ScrapingTaskSerializer, ContentSerializer
from .models import ScrapingTask, Content
from rest_framework import status
from .scrapper import scrape_and_store
from .schedule import schedule_scraping_task, remove_scheduled_task, update_task_schedule
from .es_client import es, INDEX_NAME
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

class ScrapingTaskListCreate(generics.ListCreateAPIView):
    queryset = ScrapingTask.objects.all()
    serializer_class = ScrapingTaskSerializer


    @extend_schema(
        summary="List all scraping tasks",
        description="Create a new scraping task or list all existing tasks.",
        responses={201: ScrapingTaskSerializer}
    )

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.validated_data['is_active'] = True

        scraping_task = serializer.save()

        # scrape_and_store.delay(scraping_task.id)
        schedule_scraping_task(scraping_task.id)

        return Response(serializer.data, status=201)



    @extend_schema(
        summary="Delete all scraping tasks",
        description="Delete all existing scraping tasks.",
        responses={204: None, 404:{"description": "No tasks to delete"}}
    )
    def delete(self, request):

        tasks = ScrapingTask.objects.all()
        PeriodicTask.objects.all().delete()
        IntervalSchedule.objects.all().delete()
        if tasks:

            tasks.delete()
            return Response({"message": "All tasks deleted"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"message": "No tasks to delete"}, status=status.HTTP_404_NOT_FOUND)


class ScrapingTaskDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ScrapingTask.objects.all()
    serializer_class = ScrapingTaskSerializer

    @extend_schema(
            summary="Update a scraping task",
            description="Updates a scraping task and reschedules it if necessary",
    )
    def update(self, request, *args, **kwargs):

        partial = kwargs.pop('partial', True)
        instance = self.get_object()

        was_active = instance.is_active
        old_end_time = instance.end_time

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        instance.refresh_from_db()


        if was_active != instance.is_active or old_end_time != instance.end_time:
            update_task_schedule(instance.id, instance.is_active)


        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        remove_scheduled_task(instance.id)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class ScrapingTaskContentList(generics.ListAPIView):
    serializer_class = ContentSerializer

    @extend_schema(
        summary="Get content for a specific scraping task",
        description="Returns all content items scraped by the specified task"
    )
    def get_queryset(self):
        task_id = self.kwargs['pk']
        return Content.objects.filter(scraping_task_id=task_id)




class ScrappingTaskElasticSearchList(APIView):

    @extend_schema(
        summary="Search content for a specific task",
        description="Search and filter content from a specific scraping task using Elasticsearch",
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search term to look for in title, author, location, time, and story'
            ),
            OpenApiParameter(
                name='author',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by author name'
            ),
            OpenApiParameter(
                name='author_location',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by author location'
            ),
            OpenApiParameter(
                name='published_time_from',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='Filter articles published after this date (ISO format)'
            ),
            OpenApiParameter(
                name='published_time_to',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='Filter articles published before this date (ISO format)'
            ),
            OpenApiParameter(
                name='sort_by_published_time',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Sort by published time (asc/desc)'
            ),
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "task_category": {"type": "string"},
                    "total_articles": {"type": "integer"},
                    "search_params": {"type": "object"},
                    "articles": {"type": "array"}
                }
            },
            404: {"description": "Scraping task not found"},
            500: {"description": "Internal server error"}
        }
    )

    def get(self, request, pk):

        try:
            scraping_task = ScrapingTask.objects.get(id=pk)

            search_term = request.query_params.get('search', '')
            author = request.query_params.get('author', '')
            author_location = request.query_params.get('author_location', '')
            published_time_from = request.query_params.get('published_time_from', '')
            published_time_to = request.query_params.get('published_time_to', '')
            sort_by = request.query_params.get('sort_by_published_time', '')
            print(f"Search Term: {search_term}, Author: {author}, Author Location: {author_location}, Published Time From: {published_time_from}, Published Time To: {published_time_to}, Sort By: {sort_by}")


            main_conditions = [{"match": {"category": scraping_task.category}}]

            if search_term:
                additional_conditions = [
                    {"match_phrase":{"inner_title": {"query": search_term, "boost": 3}}},
                    {"match_phrase":{"author": {"query": search_term, "boost": 2}}},
                    {"match_phrase":{"author_location": {"query": search_term, "boost": 1.5}}},
                    {"match_phrase":{"published_time_bn": {"query": search_term, "boost": 1.5}}},
                    {"match_phrase":{"main_story": {"query": search_term, "boost": 1}}}
                ]
                # main_conditions.extend(additional_conditions)
                main_conditions.append({"bool": {"should": additional_conditions}})

            if author:
                main_conditions.append({"match": {"author": author}})
            if author_location:
                main_conditions.append({"match": {"author_location": author_location}})

            filter_conditions = [{"exists" : {"field": "published_time"}}]


            if published_time_from or published_time_to:
                date_range = {}
                if published_time_from:
                    date_range["gte"] = published_time_from
                if published_time_to:
                    date_range["lte"] = published_time_to
                filter_conditions.append({"range": {"published_time": date_range}})

            
        

            query = {
                "query": {
                    "bool": {
                        "must": main_conditions,
                        "filter": filter_conditions
                    }
                },
                "size": 10000  
            }

            if sort_by:    
                query["sort"] = [{
                    "published_time": {
                        "order": sort_by.lower(),
                        "missing": "_last"
                    }
                }]

            print(f"Elasticsearch query: {query}")

            search_results = es.search(index=INDEX_NAME, body=query)
            hits = search_results.get('hits', {}).get('hits', [])
            articles = [hit['_source'] for hit in hits]

            return Response({
                "task_id": pk,
                "task_category": scraping_task.category,
                "total_articles": len(articles),
                "search_params": {
                    "search_term": search_term,
                    "author": author,
                    "author_location": author_location,
                    "published_time_from": published_time_from,
                    "published_time_to": published_time_to,
                    "sort_by_published_time": sort_by
                },
                "articles": articles
            })

        except ScrapingTask.DoesNotExist:
            return Response({"error": "Scraping task not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class GenericElasticSearchList(APIView):

    @extend_schema(
        summary="Search all content",
        description="Search and filter all content across all scraping tasks using Elasticsearch",
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search term to look for in title, author, location, time, and story'
            ),
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by category'
            ),
            OpenApiParameter(
                name='author',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by author name'
            ),
            OpenApiParameter(
                name='author_location',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by author location'
            ),
            OpenApiParameter(
                name='published_time_from',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='Filter articles published after this date (ISO format)'
            ),
            OpenApiParameter(
                name='published_time_to',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='Filter articles published before this date (ISO format)'
            ),
            OpenApiParameter(
                name='sort_by_published_time',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Sort by published time (asc/desc)'
            ),
        ]
    )


    def get(self, request):

        try:

            search_term = request.query_params.get('search', '')
            category = request.query_params.get('category', '')
            author = request.query_params.get('author', '')
            author_location = request.query_params.get('author_location', '')
            published_time_from = request.query_params.get('published_time_from', '')
            published_time_to = request.query_params.get('published_time_to', '')
            sort_by = request.query_params.get('sort_by_published_time', '')
            print(f"Search Term: {search_term}, Author: {author}, Author Location: {author_location}, Published Time From: {published_time_from}, Published Time To: {published_time_to}, Sort By: {sort_by}")

            if category:
                main_conditions = [{"match": {"category": category}}]
            else:
                main_conditions = []

            if search_term:
                additional_conditions = [
                    {"match_phrase":{"inner_title": {"query": search_term, "boost": 3}}},
                    {"match_phrase":{"author": {"query": search_term, "boost": 2}}},
                    {"match_phrase":{"author_location": {"query": search_term, "boost": 1.5}}},
                    {"match_phrase":{"published_time_bn": {"query": search_term, "boost": 1.5}}},
                    {"match_phrase":{"main_story": {"query": search_term, "boost": 1}}}
                ]
                # main_conditions.extend(additional_conditions)
                main_conditions.append({"bool": {"should": additional_conditions}})

            if author:
                main_conditions.append({"match": {"author": author}})
            if author_location:
                main_conditions.append({"match": {"author_location": author_location}})

            filter_conditions = [{"exists" : {"field": "published_time"}}]


            if published_time_from or published_time_to:
                date_range = {}
                if published_time_from:
                    date_range["gte"] = published_time_from
                if published_time_to:
                    date_range["lte"] = published_time_to
                filter_conditions.append({"range": {"published_time": date_range}})

            
        

            query = {
                "query": {
                    "bool": {
                        "must": main_conditions,
                        "filter": filter_conditions
                    }
                },
                "size": 10000  
            }

            if sort_by:    
                query["sort"] = [{
                    "published_time": {
                        "order": sort_by.lower(),
                        "missing": "_last"
                    }
                }]

            print(f"Elasticsearch query: {query}")

            search_results = es.search(index=INDEX_NAME, body=query)
            hits = search_results.get('hits', {}).get('hits', [])
            articles = [hit['_source'] for hit in hits]

            return Response({
                "total_articles": len(articles),
                "search_params": {
                    "search_term": search_term,
                    "author": author,
                    "author_location": author_location,
                    "published_time_from": published_time_from,
                    "published_time_to": published_time_to,
                    "sort_by_published_time": sort_by
                },
                "articles": articles
            })

        except ScrapingTask.DoesNotExist:
            return Response({"error": "Scraping task not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class ContentListCreate(generics.ListCreateAPIView):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
