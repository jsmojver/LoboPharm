from django.db import models

# Create your models here.

import settings

class Artikal(models.Model):
    naziv = models.CharField(max_length=128, null=True)
    mj = models.CharField(max_length=10, null=True)
    trziste = models.CharField(max_length=64)
    eskulapid = models.IntegerField(blank=True, null=True)
    pakiranje = models.CharField(max_length=25, null=True)

    class Meta:
        db_table = u'ARTIKLI'

class PonudeZ(models.Model):
    narudzbaid = models.IntegerField(blank=True, null=True)
    datum = models.DateField()
    kupacid = models.IntegerField(blank=True, null=True)
    kupac = models.CharField(max_length=128, null=True)
    adresa = models.CharField(max_length=192, null=True)
    statuseskulap = models.IntegerField(blank=True, null=True)
    statusidema = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = u'PONUDEZ'

class PonudeS(models.Model):
    ponuda = models.ForeignKey(PonudeZ, null=True, blank=True, related_name='stavke', db_column='ponudaid')
    #ponudaid = models.IntegerField(blank=True, null=True)
    rbr = models.IntegerField(blank=True, null=True)
    artikalid = models.IntegerField(blank=True, null=True)
    trziste = models.CharField(max_length=64)
    kolicina = models.DecimalField(max_digits=10, decimal_places=2)
    mpcijena = models.DecimalField(max_digits=10, decimal_places=2)
    pdv = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = u'PONUDES'
