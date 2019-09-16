# # Python Code
# # project/myapp/tasks.py

# import datetime
# import celery

# @celery.decorators.periodic_task(run_every=datetime.timedelta(minutes=1)) # here we assume we want it to be run every 5 mins
# def myTask():
#     # Do something here
#     # like accessing remote apis,
#     # calculating resource intensive computational data
#     # and store in cache
#     # or anything you please
#     print('This wasn\'t so difficult')


# Python Code
# myapp/management/commands/mytask.py

from django.core.management.base import BaseCommand, CommandError
from polls.models import Question as Poll

class Command(BaseCommand):
    help = 'Type the help text here'

    def handle(self, *args, **options):
        # Add yout logic here
        # This is the task that will be run
        print('ccc')
        self.stdout.write('This was extremely simple!!!')