
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json


def schedule_scraping_task(task_id):
    from .models import ScrapingTask
    # from django.utils import timezone
    # import pytz


    scraping_task = ScrapingTask.objects.get(id=task_id)


    # end_time = scraping_task.end_time
    # if end_time and not timezone.is_aware(end_time):
    #     end_time = timezone.make_aware(end_time)
    # end_time = end_time.astimezone(pytz.UTC)

    interval, _ = IntervalSchedule.objects.get_or_create(
        every=scraping_task.scheduled_hours,
        period=IntervalSchedule.MINUTES,
    )

    PeriodicTask.objects.create(
        interval=interval,
        name=f'Scraping Task {task_id}',
        task='api.scrapper.scrape_and_store',
        args=json.dumps([task_id]),
        one_off=False,
        enabled=scraping_task.is_active,
        expires=scraping_task.end_time,
    )


def remove_scheduled_task(task_id):

    task_name = f'Scraping Task {task_id}'
    PeriodicTask.objects.filter(name=task_name).delete()


def update_task_schedule(task_id, is_active):
    from .models import ScrapingTask
    task_name = f'Scraping Task {task_id}'
    
    try:
        scraping_task = ScrapingTask.objects.get(id=task_id)
        
        periodic_task = PeriodicTask.objects.get(name=task_name)
        periodic_task.enabled = is_active
        periodic_task.expires = scraping_task.end_time

        interval, _ = IntervalSchedule.objects.get_or_create(
            every=scraping_task.scheduled_hours,
            period=IntervalSchedule.MINUTES,
        )
        periodic_task.interval = interval

        periodic_task.save()
        return True
    

    except PeriodicTask.DoesNotExist:
        if is_active:
            schedule_scraping_task(task_id)
        return False