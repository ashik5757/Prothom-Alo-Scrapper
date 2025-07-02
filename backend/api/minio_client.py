import boto3
import os
import logging
import requests
from botocore.config import Config
from botocore.exceptions import ClientError
from urllib.parse import urlparse
import hashlib


logger = logging.getLogger(__name__)


# MinIO configuration
MINIO_ENDPOINT = 'http://minio:9000'
MINIO_ACCESS_KEY = 'minioadmin'
MINIO_SECRET_KEY = 'minioadmin'
BUCKET_NAME = 'prothom-alo-scrapper'


s3_client = boto3.client(
    's3',
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    region_name='asia-south1',
)


def create_bucket_if_not_exists():
    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        logger.info(f"Bucket '{BUCKET_NAME}' already exists.")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            try:
                s3_client.create_bucket(Bucket=BUCKET_NAME)
                logger.info(f"Bucket '{BUCKET_NAME}' created successfully.")
            except ClientError as e:
                logger.error(f"Failed to create bucket '{BUCKET_NAME}': {e}")
        else:
            logger.error(f"Error checking bucket '{BUCKET_NAME}': {e}")



def upload_main_story(content_id, main_story, published_time):
    
    try:
        from datetime import datetime

        if published_time:
            if isinstance(published_time, str):
                try:
                    dt = datetime.fromisoformat(published_time.replace('Z', '+00:00'))
                except ValueError as e:
                    dt = datetime.fromisoformat(published_time.split('+')[0].split('Z')[0])
            else:
                dt = published_time

            year = dt.strftime('%Y')
            month = dt.strftime('%m')
            day = dt.strftime('%d')
        
        else:
            now = datetime.now()
            year = now.strftime('%Y')
            month = now.strftime('%m')
            day = now.strftime('%d')

        s3_key = f"articles/{year}/{month}/{day}/{content_id}/main_story.txt"
    
        create_bucket_if_not_exists()

        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=main_story.encode('utf-8'),
            ContentType='text/plain'
        )

        logger.info(f"Successfully uploaded main story for content {content_id} to {s3_key}")
        return s3_key

    except Exception as e:
        logger.error(f"Error uploading main story for content {content_id}: {e}")
        return None



def get_main_story(s3_key):
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=s3_key)
        main_story = response['Body'].read().decode('utf-8')
        return main_story

    except Exception as e:
        logger.error(f"Error getting main story for key {s3_key}: {e}")
        return None
    






def download_image_from_url(image_url):
    try:
        if image_url.startswith('//'):
            image_url = "https:" + image_url
        elif not image_url.startswith(('http://', 'https://')):
            image_url = "https://" + image_url

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        response = requests.get(image_url, headers=headers, timeout=30)
        response.raise_for_status()  

        return response.content

    except Exception as e:
        logger.error(f"Error processing image URL {image_url}: {e}")
        return None



def get_image_extension(image_url):
    try:
        parsed_url = urlparse(image_url)
        path = parsed_url.path.lower()

        if '.jpg' in path or '.jpeg' in path:
            return '.jpg'
        elif '.png' in path:
            return '.png'
        elif '.gif' in path:
            return '.gif'
        elif '.webp' in path:
            return '.webp'
        elif '.svg' in path:
            return '.svg'
        else:
            return '.jpg'
        

    except Exception as e:
        logger.error(f"Error getting image extension from URL {image_url}: {e}")
        return '.jpg' 



def upload_image(content_id, image_url, image_type, published_time, image_index=0):

    try:
        from datetime import datetime
        

        image_data = download_image_from_url(image_url)
        if not image_data:
            return None
            

        if published_time:
            if isinstance(published_time, str):
                try:
                    dt = datetime.fromisoformat(published_time.replace('Z', '+00:00'))
                except ValueError:
                    dt = datetime.fromisoformat(published_time.split('+')[0].split('Z')[0])
            else:
                dt = published_time
                
            year = dt.strftime('%Y')
            month = dt.strftime('%m')
            day = dt.strftime('%d')
        else:
            now = datetime.now()
            year = now.strftime('%Y')
            month = now.strftime('%m')
            day = now.strftime('%d')
    
        file_extension = get_image_extension(image_url)
        url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]


        if image_type == 'cover':
            filename = f"cover_image{file_extension}"
            s3_key = f"images/{year}/{month}/{day}/{content_id}/{filename}"
        else:
            filename = f"story_image_{image_index}_{url_hash}{file_extension}"
            s3_key = f"images/{year}/{month}/{day}/{content_id}/{filename}"

        # filename = f"story_image_{image_index}_{url_hash}{file_extension}"
        # s3_key = f"articles/{year}/{month}/{day}/{content_id}/{filename}"
    
        create_bucket_if_not_exists()

        content_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.avif': 'image/avif',
            '.svg': 'image/svg+xml'
        }
        content_type = content_type_map.get(file_extension, 'image/jpeg')

        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=image_data,
            ContentType=content_type,
            Metadata={
                'original_url': image_url,
                'image_type': image_type,
                'content_id': str(content_id)
            }
        )
        
        logger.info(f"Successfully uploaded {image_type} image for content {content_id} to {s3_key}")
        return s3_key
    
    except Exception as e:
        logger.error(f"Error uploading {image_type} image for content {content_id}: {e}")
        return None



def upload_multiple_images(content_id, image_urls_data, published_time):

    uploaded_images = {
        'cover_image_path': None,
        'story_images_paths': []
    }


    try:
        if image_urls_data.get('cover_image'):
            cover_path = upload_image(
                content_id=content_id,
                image_url=image_urls_data['cover_image'],
                image_type='cover',
                published_time=published_time,
                image_index=0
            )
            uploaded_images['cover_image_path'] = cover_path
        
        
        story_images = image_urls_data.get('story_images', [])
        for index, image_url in enumerate(story_images):
            story_path = upload_image(
                content_id=content_id,
                image_url=image_url,
                image_type='story',
                published_time=published_time,
                image_index=index
            )

            if story_path:
                uploaded_images['story_images_paths'].append(story_path)
        

    except Exception as e:
        logger.error(f"Error uploading images for content {content_id}: {e}")
        return uploaded_images

    return uploaded_images


def delete_image(s3_key):

    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=s3_key)
        logger.info(f"Successfully deleted image at {s3_key}")
        return True
    except ClientError as e:
        logger.error(f"Error deleting image at {s3_key}: {e}")
        return False

