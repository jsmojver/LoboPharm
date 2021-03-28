import os, sys

sys.path.append('/home/hrvoje/Programming')
sys.path.append('/home/hrvoje/Programming/diocles')

os.environ['DJANGO_SETTINGS_MODULE'] = 'diocles.settings'
os.environ['LC_NUMERIC']='en_US.UTF-8'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

