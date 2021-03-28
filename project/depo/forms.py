from django import forms

from depo.models import *

from django.forms import Form, ModelForm
from django.forms.formsets import formset_factory

class PosiljkaForm(ModelForm):
  class Meta:
    model = Posiljka

class PosiljkaLijekForm(ModelForm):
  class Meta:
     model = PosiljkaLijek

class ZahtjevForm(Form):
  lijekId = forms.IntegerField()  
  kolicina = forms.IntegerField()
  opaska = forms.CharField(widget=forms.widgets.Textarea(), required=False)

