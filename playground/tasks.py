from time import sleep
from celery import shared_task


@shared_task
def notify_customers(message: str):
    print(message)
    print("Sending 10k mails...")
    sleep(10)
    print("Success.")
