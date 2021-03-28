import os, sys

sys.path.append("/var/www/diocles")
sys.path.append("/var/www/diocles/project")

os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'
os.environ['LC_NUMERIC']='en_US.UTF-8'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
