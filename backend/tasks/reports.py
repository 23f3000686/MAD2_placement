from celery_worker import celery


@celery.task

def monthly_report():

    print("Generating placement report")