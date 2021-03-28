from django.db import models

# Create your models here.

from django.db import models
from django.forms import ModelForm, Textarea, TextInput, HiddenInput
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from decimal import Decimal

from stdnum.iso7064 import mod_11_10 # Za provjeru OIB-a, VBDI i broja računa

from meds.models import *
from fiskalizacija.models import *
from order.models import *

from django.db.models import Q

################### MODEL VALIDATORS #########################

def validate_iso7064(value):
  from django.core.validators import ValidationError
  if not mod_11_10.is_valid(value) and value:
    raise ValidationError('Broj je neispravan, molimo provjerite!')

##############################################################

class Blagajna(models.Model):
  radno_mjesto = models.CharField(max_length=64, null=True, blank=True)

class BlagajnaArtikal(models.Model):
  TIP = { 0 : 'Narudžba', 1: 'Depo', 2: 'Lager'}

  cijena = models.DecimalField(max_digits=12, decimal_places=2)
  kolicina = models.IntegerField()
  created = models.DateTimeField(auto_now_add=True)
  modified = models.DateTimeField(auto_now=True)



