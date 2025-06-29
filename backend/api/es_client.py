
from elasticsearch import Elasticsearch

es = Elasticsearch("http://elasticsearch:9200")
INDEX_NAME = "prothomalo_articles"


def create_index_with_mapping():
    try:

        if not es.indices.exists(index=INDEX_NAME):
            
            mapping = {
                "mappings": {
                    "properties": {
                        "title": {"type": "text"},
                        "url": {"type": "keyword"},
                        "category": {"type": "keyword"},
                        "inner_title": {"type": "text"},
                        "author": {"type": "text"},
                        "author_location": {"type": "text"},
                        "published_time": {"type": "date", "format": "strict_date_optional_time||yyyy-MM-dd'T'HH:mm:ssXXX"},
                        "published_time_bn": {"type": "text"},
                        "main_story": {"type": "text"}
                    }
                }
            }
            es.indices.create(index=INDEX_NAME, body=mapping)
            print(f"Created index {INDEX_NAME} with proper mappings")
        else:
            print(f"Index {INDEX_NAME} already exists")
    except Exception as e:
        print(f"Error creating Elasticsearch index: {e}")




create_index_with_mapping()
