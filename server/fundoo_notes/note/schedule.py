from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json
from loguru import logger
from note.tasks import send_reminder_email


def schedule_reminder(note):
    try:
        # Convert datetime to cron format
        reminder_time = note.reminder
        cron_minute = reminder_time.minute
        cron_hour = reminder_time.hour
        cron_day = reminder_time.day
        cron_month = reminder_time.month
        cron_day_of_week = reminder_time.weekday()

        logger.info(f'Scheduling reminder for note ID {note.id} at {reminder_time}.')

        # Create a schedule
        schedule, created = CrontabSchedule.objects.get_or_create(
            minute=cron_minute,
            hour=cron_hour,
            day_of_month=cron_day,
            month_of_year=cron_month,
            day_of_week="*",
        )
        if created:
            logger.info(f'Created new CrontabSchedule: {schedule}.')
        else:
            logger.info(f'Using existing CrontabSchedule: {schedule}.')

        # Create or update the periodic task
        periodic_task, created = PeriodicTask.objects.update_or_create(
            name=f"send_reminder_email_{note.id}",
            defaults={
                'crontab': schedule,
                'task': 'note.tasks.send_reminder_email',
                'args': json.dumps([note.title,note.user.email]),
            }
        )
        if created:
            logger.info(f'Created new PeriodicTask: {periodic_task}.')
        else:
            logger.info(f'Updated existing PeriodicTask: {periodic_task}.')

    except Exception as e:
        logger.error(f'Error scheduling reminder for note ID {note.id}: {e}')