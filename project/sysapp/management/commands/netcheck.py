from django.core.management.base import BaseCommand, CommandError
from fiskalizacija.flib import *
from sysapp.models import StatusVeze

import urllib2

def internet_on():
    try:
        response=urllib2.urlopen('http://www.google.com',timeout=3)
        return True
    except urllib2.URLError as err: pass
    return False

class Command(BaseCommand):
    args = '<netceck ...>'
    help = 'Check Diocles network connectivity'

    def handle(self, *args, **options):

      r = Fiskalizacija()
      start_time = time.time()
      greska = ''
      try:
        r.echo()
      except Exception, e:
        greska = e
        exec_time = time.time() - start_time
  
      status, created = StatusVeze.objects.get_or_create(id=1)
      if r.echo_response[0] == 200 and 'ping' in r.echo_response[1]:
        status.cis = True
      else:
        status.cis = False

      status.vpn = 0
      status.net = internet_on()
      status.save()

      # TODO: ovo je samo za debug, inace se pokrece iz CRON-a
      self.stdout.write('Provjeravam vezu %s\n\n' % status.cis)

          #  return HttpResponse('{"Status": "%s", "Response": "%s", "exec_time": "%s", "greska": "%s"}' % (r.echo_response[0], r.echo_response[1], exec_time, greska))

