from django.utils import timezone

from celery import shared_task

from habits.services import send_message_telegram
from users.models import User



@shared_task
def send_message_user():
    now = timezone.now()
    for user in User.objects.all():
        if user.habits.all().exists() and user.is_active and user.tg_chat_id:
            for habit in user.habits.filter(time__date=now.date()):
                send_message_telegram(f"На сегодня у вас запланирована привычка: {habit}", user.tg_chat_id)
