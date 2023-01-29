"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
import threading

from django.core.wsgi import get_wsgi_application
from stock.requester import request_sales

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = get_wsgi_application()

requester_sales = threading.Thread(target=request_sales, daemon=True)
requester_sales.start()
