#!/usr/bin/python
# -*- coding: utf8 -*-


import csv, commands, sys, os, subprocess, re, datetime
from django.core.management import call_command 


os.environ['DJANGO_SETTINGS_MODULE'] = "settings"

from django.db.models import Sum

from meds.models import *
from order.models import *
from depo.models import *

ukupno = 0
for i in Lijek.objects.all():
    izdano = Stavka.objects.filter(artikal__id=i.id).aggregate(Sum('kolicina')).values()[0]
    primljeno = sum(i.depo_posiljka_lijekovi.values_list('kolicina', flat=True))
    steta = 0
    try: 
      razlika = primljeno - izdano - i.stanje
      steta = abs(razlika * i.cijena)
      ukupno = ukupno + steta

    except: pass
    try: print '%s (id %s) primljeno je %s, a izdano %s. Moglo je biti izdano najvise %s. Trenutno stanje je %s, pocetno stanje treba biti %s, steta %s' % (i.naziv, i.id, primljeno, izdano, (primljeno-i.stanje), i.stanje, abs(primljeno-izdano-i.stanje), steta)
    except: pass

print 'Ukupna razlika = %s Eur' % ukupno 

########################################################################

ukupno = 0
for i in Lijek.objects.all():
  iznos = sum(i.depo_posiljka_lijekovi.values_list('kolicina', flat=True))
  cijena = iznos * i.cijena
  ukupno = ukupno + cijena
  # print '%s Euro' % cijena
print 'Ukupno naruceno: %s' % ukupno

ukupno_izdano = 0
for i in Lijek.objects.all():
  try: 
    iznos = Stavka.objects.filter(artikal__id=i.id).aggregate(Sum('kolicina')).values()[0]
    cijena = iznos * i.cijena
    ukupno_izdano = ukupno_izdano + cijena
  except: pass
  # print '%s Euro' % cijena
print 'Ukupno izdano: %s' % ukupno_izdano

inventar = 0
for i in Lijek.objects.all():
  inventar = inventar + i.stanje * i.cijena

print 'Razlika: %s' % (ukupno - ukupno_izdano)
print 'Inventurna vrijednost: %s' % inventar
print 'Nedostaje: %s' % (inventar - (ukupno - ukupno_izdano))


ukupno = 0
for i in Lijek.objects.all():
  try: iznos = sum(i.depo_posiljka_lijekovi.values_list('kolicina', flat=True))
  except: iznos = 0

  cijena = iznos * i.cijena

  try: drugi_iznos = Stavka.objects.filter(artikal__id=i.id).aggregate(Sum('kolicina')).values()[0]
  except: drugi_iznos = 0
  
  try: razlika = int(iznos) - int(drugi_iznos)
  except: razlika = int(iznos)

  steta = (razlika - i.stanje) * i.cijena
  print "Za lijek %s po paketima bilo je %s a po stavkama %s - Ocekivano stanje: %s, knjizeno na stanju: %s" % (i.naziv, iznos, drugi_iznos, razlika, i.stanje)
  if razlika == i.stanje:
    print "    Za lijek %s slazu se stanje i prometi" % i.naziv

  ukupno = ukupno + steta

print 'Ukupno odstupanje %s' % ukupno
