# File: myproject/myproject/wsgi.py

import os

from django.core.wsgi import get_wsgi_application

# Point this to your settings module:
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")

# The WSGI application object that Gunicorn, uWSGI, etc. will use:
application = get_wsgi_application()
