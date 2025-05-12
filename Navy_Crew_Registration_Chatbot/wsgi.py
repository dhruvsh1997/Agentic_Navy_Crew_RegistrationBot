"""
WSGI config for Navy_Crew_Registration_Chatbot project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Navy_Crew_Registration_Chatbot.settings')

application = get_wsgi_application()
