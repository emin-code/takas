"""
WSGI config for takasonline project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'takasonline.settings')

application = get_wsgi_application() 