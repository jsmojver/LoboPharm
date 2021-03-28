#coding=utf-8


from django.db import models
from django import forms

from order.models import * 
from project.common_models import AdminSetter

import settings

    
class AbdaIndikacija(models.Model):
  sifra = models.CharField(max_length=5, db_index=True)
  parent = models.ForeignKey('self', related_name='children', null=True)
  opis = models.CharField(max_length=96)
  verweisfl = models.BooleanField()

class AtcCode(models.Model):
  sifra = models.CharField(max_length=7, db_index=True)
  parent = models.ForeignKey('self', related_name='children', null=True)
  opis = models.CharField(max_length=120, null=True)

  def tablica(self):
    
    ret = []
    obj = self
    ret.append((obj.sifra, obj.opis))
    while obj.parent.id != 1:
      ret.append((obj.parent.sifra, obj.parent.opis))
      obj = obj.parent
    ret.reverse()
    return ret

class Interaktionstext(models.Model):
  TIP = {
    1: "Opis",
    2: "Opis",
    3: "erwartet",
    4: "erwartet",
    5: "keine Aussage moglich",
    6: "keine Aussage moglich",
    7: "unwahrscheinlich",
    8: "unwahrscheinlich",
    9: "Literatura",
    40: "Farmakološki efekt",
    100: "Važna napomena",
    110: "Mjere",
    140: "Mehanizam"}
  text = models.TextField(db_column='Interaktionstext', blank=True) 
  tip = models.IntegerField()   
  class Meta:
    db_table = u'abda_Interaktionstext'
  
  def tip_naziv(self):
    try: return self.TIP[self.tip]
    except: pass

class FamAnbieter(models.Model):
  id = models.IntegerField(primary_key=True) 
  staatkuerzel = models.CharField(max_length=10, null=True, blank=True)
  postcode = models.CharField(max_length=10, null=True, blank=True)
  postfachcode = models.CharField(max_length=10, null=True, blank=True)
  name = models.CharField(max_length=105, null=True, blank=True)
  postfach = models.CharField(max_length=15, null=True, blank=True)
  telefon = models.CharField(max_length=20, null=True, blank=True)
  telefax = models.CharField(max_length=20, null=True, blank=True)
  strasse = models.CharField(max_length=50, null=True, blank=True)
  ort = models.CharField(max_length=50, null=True, blank=True)
  postfachort = models.CharField(max_length=50, null=True, blank=True)
  kurzname = models.CharField(max_length=80, null=True, blank=True)
  suchbegriffkurzname = models.CharField(max_length=80, null=True, blank=True)

  class Meta:
    db_table = u'abda_Fertigarzneimittelanbieter'
  
class Interaktion(models.Model): 
  OZBILJNOST = {
    1: "OPREZ, moguće ozbiljne posljedice",
    2: "Oprez, ne preporučuje se uzimati zajedno",
    3: "Preporučuje se nadzor liječnika",
    4: "Preporučuje se nadzor liječnika",
    5: "Preporučuje se nadzor liječnika",
    6: "Osobite mjere nisu potrebne"}
  id = models.IntegerField(primary_key=True) 
  interaktionnr = models.IntegerField(null=True, db_column='InteraktionNr', blank=True, db_index=True) 
  bezeichnunglinks = models.CharField(max_length=300, db_column='BezeichnungLinks', blank=True) 
  bezeichnungrechts = models.CharField(max_length=300, db_column='BezeichnungRechts', blank=True) 
  aktualisiertam = models.IntegerField(null=True, db_column='AktualisiertAm', blank=True) 
  klinischebedeutung = models.IntegerField(null=True, db_column='KlinischeBedeutung', blank=True) 
  effektkurz = models.CharField(max_length=600, db_column='EffektKurz', blank=True) 
  mechanismusdynamischkurz = models.CharField(max_length=600, db_column='MechanismusDynamischKurz', blank=True) 
  kenntnisstanddynamisch = models.IntegerField(null=True, db_column='KenntnisstandDynamisch', blank=True) 
  mechanismuskinetischkurz = models.CharField(max_length=600, db_column='MechanismusKinetischKurz', blank=True) 
  kenntnisstandkinetisch = models.IntegerField(null=True, db_column='KenntnisstandKinetisch', blank=True) 
  mechanismussonstigkurz = models.CharField(max_length=600, db_column='MechanismusSonstigKurz', blank=True) 
  kenntnisstandsonstig = models.IntegerField(null=True, db_column='KenntnisstandSonstig', blank=True) 
  text = models.ManyToManyField(Interaktionstext)
  class Meta:
    db_table = u'abda_Interaktion'
    ordering = ['-klinischebedeutung']

  def ozbiljnost(self):
    return self.OZBILJNOST[self.klinischebedeutung]

class Stoff(models.Model):
  id = models.IntegerField(primary_key=True) 
  verschreibungspflichtfl = models.CharField(max_length=3, db_column='VerschreibungspflichtFl') 
  btmanlage = models.IntegerField(null=True, db_column='BtmAnlage', blank=True) 
  btmgundstoffkategorie = models.IntegerField(null=True, db_column='BtmGundstoffkategorie', blank=True) 
  wirkstofffl = models.BooleanField(default=0, db_column='WirkstoffFl') 
  hilfsstofffl = models.BooleanField(default=0, db_column='HilfsstoffFl') 
  costofffl = models.BooleanField(default=0, db_column='CoStoffFl') 
  chemikaliefl = models.BooleanField(default=0, db_column='ChemikalieFl') 
  lebensmittelzusatzstofffl = models.BooleanField(default=0, db_column='LebensmittelzusatzstoffFl') 
  nahrungsgenussmittelfl = models.BooleanField(default=0, db_column='NahrungsGenussmittelFl') 
  pflanzenschutzmittelfl = models.BooleanField(default=0, db_column='PflanzenschutzmittelFl') 
  inkosmetikafl = models.BooleanField(default=0, db_column='InKosmetikaFl') 
  anthroposophikumfl = models.BooleanField(default=0, db_column='AnthroposophikumFl') 
  homoeopathikumfl = models.BooleanField(default=0, db_column='HomoeopathikumFl') 
  hatderivatfl = models.BooleanField(default=0, db_column='HatDerivatFl') 
  hatverweisfl = models.BooleanField(default=0, db_column='HatVerweisFl') 
  hatzusammensetzungfl = models.BooleanField(default=0, db_column='HatZusammensetzungFl') 
  vorkommendeutschfl = models.BooleanField(default=0, db_column='VorkommenDeutschFl') 
  vorkommeninternationalfl = models.BooleanField(default=0, db_column='VorkommenInternationalFl') 
  class Meta:
    db_table = u'abda_Stoff'

  def naziv_tvari(self):
    try: return self.nazivi.get(vorzugsbezeichnungfl=1).name
    except: pass

class Stoffinteraktion(models.Model):
    stoff = models.ForeignKey(Stoff, null=True, db_column='StoffNr', blank=True, related_name='interakcije') 
    interaktion = models.ForeignKey(Interaktion, null=True, db_column='InteraktionNr', blank=True, related_name='interakcije') 
    lokalisation = models.CharField(max_length=6, db_column='Lokalisation', blank=True) 
    lr = models.IntegerField(default=0)
    class Meta:
        db_table = u'abda_Stoffinteraktion'    

class StoffText(models.Model):
  TEKSTOVI = {1: "Verschreibungspflicht, Spezifizierung zur",
              2: "BtM-Verschreibungshöchstmengen",
              3: "Stoffbeschreibung",
              4: "Anwendung",
              5: "Schmelzpunkt",
              6: "Siedepunkt",
              7: "Drehung, optische",
              8: "Brechungsindex",
              9: "Löslichkeit",
              10: "Basizität",
              11: "Dichte",
              12: "Spektroskopie",
              13: "Stabilität",
              14: "Lagerung",
              15: "Pflanzen, Vorkommen",
              16: "Pflanzen, Qualität",
              17: "I.E.-Umrechnung",
              18: "Pflanzen, Inhaltstoffe",
              19: "Maximaldosen",
              36: "BtM-Verschreibungspflicht, Ausnahmen zur",
              37: "Verschreibungspflicht, Ausnahmen zur",
              50: "Summenformel",
              51: "Molmasse",
              57: "Dampfdruck",
              58: "Dipolmoment",
              59: "Farbe",
              60: "Fettkennzahlen",
              61: "Flammpunkt",
              62: "Halbwertszeit",
              63: "Isoelektrischer Punkt",
              64: "Kritische Werte",
              65: "Sublimation",
              66: "Viskosität",
              67: "Wasserverlust",
              69: "Doping",
              70: "Grundstoffe GÜG"}

  id = models.IntegerField(primary_key=True) 
  stoff = models.ManyToManyField(Stoff, related_name='text')
  tip = models.IntegerField(blank=True, null=True)
  text = models.TextField(db_column='Stofftext', blank=True)
  class Meta:
    db_table = u'abda_Stofftext'
    
  def get_tekst(self):
    return self.TEKSTOVI[self.tip]

class Stoffname(models.Model):
    stoff = models.ForeignKey(Stoff, null=True, blank=True, related_name='nazivi') 
    sortnr = models.IntegerField(null=True, db_column='SortNr', blank=True) 
    vorzugsbezeichnungfl = models.BooleanField(default=0, db_column='VorzugsbezeichnungFl') 
    name = models.TextField(db_column='Name', blank=True) 
    suchbegriff = models.CharField(max_length=1530, db_column='Suchbegriff', blank=True, db_index=True) 
    sortierbegriff = models.CharField(max_length=180, db_column='Sortierbegriff', blank=True) 
    stoffnamensherkunftnr = models.IntegerField(null=True, db_column='StoffnamensherkunftNr', blank=True) 
    class Meta:
        db_table = u'abda_Stoffname'

class Fertigarzneimitteltext(models.Model):
    TIPOVI = {10: "Svojstva",
              20: "Područje primjene (Indikacije)",
              30: "Kontraindikacije",              
              40: "Nuspojave",
              50: "Zabilješka",
              60: "Doziranje",
              70: "Skladištenje i trajnost",
              99: "Primjedbe pacijenata"}
      
    tekst = models.TextField(db_column='Fertigarzneimitteltext', blank=True) 
    izmijenjeno = models.DateField(blank=True, null=True)
    tip = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = u'abda_Fertigarzneimitteltext'              
       
    def get_tip(self):
      return self.TIPOVI[self.tip]           

class Fertigarzneimittel(models.Model): 

    drflookup = { "ABL":"Aufbewahrungslösung", "ABR":"Aufbewahrungs- und Reinigungslösung", "AEO":"Ätherisches Öl", "AER":"Aerosol", "AFL":"Ampullenflaschen", "AIM":"Ampullen i.m.", "AIV":"Ampullen i.v.", "AMP":"Ampullen", "ANS":"Analsalbe", "AOT":"Augen- und Nasentropfen", "APA":"Ampullenpaare", "ASN":"Augen- und Nasensalbe", "ASO":"Augen- und Ohrensalbe", "ATO":"Augen- und Ohrentropfen", "ATR":"Augentropfen", "AUB":"Augenbad", "AUG":"Augengel", "AUS":"Augensalbe", "BAD":"Bad", "BAL":"Balsam", "BAN":"Bandage", "BAO":"Badeöl", "BEU":"Beutel", "BFS":"Basisfettsalbe", "BIN":"Binden", "BIS":"Bissen", "BNM":"Benetzungsmittel", "BOH":"Bohnen", "BON":"Bonbons", "BPL":"Basisplatte", "BRE":"Brei", "BRG":"Brausegranulat", "BRT":"Buccal Retard-Tabletten", "BSC":"Basiscreme", "BSL":"Badesalz", "BSS":"Basissalbe", "BTA":"Brausetabletten", "COM":"Compretten", "CRE":"Creme", "DAM":"Doppelampullen", "DDR":"Depot-Dragees", "DEP":"Dentalpaste", "DES":"Destillat", "DFL":"Durchstechflaschen", "DIL":"Dilution", "DKA":"Dragees in Kalenderpackung", "DLS":"Desinfektionslösung", "DOS":"Dosieraerosol", "DPK":"Depot-Kapseln", "DPS":"Depot-Suspension", "DRA":"Dragees", "DRM":"Dragees magensaftresistent", "DSC":"Dosierschaum", "DSS":"Dosierspray", "DTA":"Depot-Tabletten", "EDP":"Einzeldosispipetten", "EIN":"Einreibung", "ELE":"Elektroden", "ELI":"Elixier", "EMU":"Emulsion", "ESS":"Essenz", "ESU":"Erw.-Suppositorien", "EXT":"Extrakt", "FBD":"Fußbad", "FBE":"Filterbeutel", "FBL":"Fußbalsam", "FBW":"Franzbranntwein", "FCR":"Fußcreme", "FDA":"Filmdragees", "FER":"Fertigspritzen", "FET":"Fettsalbe", "FIL":"Film", "FLA":"Flaschen", "FLU":"Flüssigkeit", "FOL":"Folie", "FSE":"Flüssigseife", "FSP":"Fuß-Spray", "FTA":"Filmtabletten", "GAB":"Gazebinden", "GAZ":"Gaze", "GEE":"Gelee", "GEL":"Gel", "GLM":"Gleitmittel", "GLO":"Globuli", "GPA":"Gelplatten", "GRA":"Granulat", "GUL":"Gurgellösung", "GWA":"Gesichtswasser", "HAB":"Halsbänder", "HAO":"Hautöl", "HAS":"Handschuhe", "HCR":"Hautcreme", "HPI":"Hautpinselung", "HSA":"Hustensaft", "HSI":"Hustensirup", "HTA":"Halstabletten", "HTR":"Hustentropfen", "HWS":"Haarwasser", "IFA":"Infusionsampullen", "IFB":"Infusionsbeutel", "IFF":"Infusionsflaschen", "IFK":"Infusionslösungskonzentrat", "IFL":"Injektionsflaschen", "IFS":"Infusionsset", "IFU":"Infusion", "IHA":"Inhalationsampullen", "IHP":"Inhalationspulver", "IIM":"Injektionsflaschen i.m.", "IKA":"Inhalationskapseln", "ILO":"Injektionslösung", "IML":"Impflanzetten", "IMP":"Implantat", "INF":"Infusionslösung", "INH":"Inhalat", "INI":"Injektions-/Infusionsflaschen", "INJ":"Injektion", "INL":"Inhalationslösung", "INS":"Instant-Tee", "IPA":"Insulinpatronen", "IST":"Instillation", "ISU":"Injektionssuspension", "IUP":"Intrauterinpessar", "KAN":"Kanüle", "KAP":"Kapseln", "KAT":"Katheter", "KDA":"Kaudragees", "KEG":"Kegel", "KER":"Kerne", "KGU":"Kaugummi", "KIT":"Kindertabletten", "KKA":"Kaukapseln", "KKS":"Kleinkdr.-Suppositorien", "KLI":"Klistiere", "KLT":"Klistiertabletten", "KLY":"Klysmen", "KMR":"Kapseln magensaftresistent", "KOA":"Konzentratampullen", "KOD":"Kondome", "KOM":"Kompressen", "KON":"Konzentrat", "KPG":"Kombipackung", "KRI":"Kristallsuspension", "KRK":"Kdr.-Rektalkapseln", "KRT":"Kräutertabletten", "KSA":"Kdr.-Saft", "KSI":"Kdr.-Sirup", "KSS":"Kdr.- u. Sgl.-Suppositorien", "KSU":"Kdr.-Suppositorien", "KTA":"Kautabletten", "KUG":"Kugeln", "KUS":"Kindersuspension", "LAN":"Lanzetten", "LEI":"Leinsamen", "LID":"Lingualdragees", "LIN":"Liniment", "LIP":"Lippenschutz", "LIQ":"Liquidum", "LMA":"Lösungsmittelampullen", "LOE":"Lösung", "LOT":"Lotion", "LTA":"Lacktabletten", "LUD":"Lutschdragees", "LUP":"Lutschpastillen", "LUT":"Lutschtabletten", "MAG":"Magentabletten", "MAO":"Massageöl", "MAS":"Massagemilch", "MDR":"Manteldragees", "MIL":"Milch", "MIX":"Mixtur", "MSA":"Mundsalbe", "MSP":"Mundspray", "MTA":"Manteltabletten", "MUG":"Mundgel", "MUT":"Mundtropfen", "MUW":"Mundwasser", "NAG":"Nasengel", "NAO":"Nasenöl", "NAS":"Nasenspray", "NDS":"Nasendosierspray", "NSA":"Nasensalbe", "NTP":"Nasentamponaden", "NTR":"Nasentropfen", "OBK":"Oblatenkapseln", "OCU":"Occusert", "OEL":"Öl", "OHT":"Ohrentropfen", "OTA":"Oblongtabletten", "OVU":"Ovula", "PAM":"Packungsmasse", "PAS":"Pastillen", "PEL":"Pellets", "PER":"Perlen", "PFL":"Pflaster", "PFT":"Pflaster transdermal", "PIL":"Pillen", "PIN":"Pinselung", "PLG":"Perlongetten", "PPL":"Pumplösung", "PRS":"Presslinge", "PSP":"Puderspray", "PST":"Paste", "PUD":"Puder", "PUL":"Pulver", "RED":"Retard-Dragees", "REK":"Retard-Kapseln", "REM":"Reinigungsmittel", "RET":"Retard-Tabletten", "RGR":"Retardgranulat", "RKA":"Rektalkapseln", "ROL":"Roller", "RSE":"Retard-Saft", "RUT":"Retardüberzogene Tabletten", "SAF":"Saft", "SAL":"Salbe", "SAV":"Salbenverband", "SCH":"Schaum", "SCM":"Schüttelmixtur", "SEI":"Seife", "SHA":"Shampoo", "SIR":"Sirup", "SKS":"Schulkdr. Suppositorien", "SLZ":"Salz", "SMT":"Schmelztabletten", "SMU":"Suppositorien mit Mulleinlage", "SOK":"Schokolade", "SOL":"Solution", "SPA":"Spritzampullen", "SPF":"Sprühflasche", "SPI":"Spiritus", "SPL":"Spüllösung", "SPR":"Spray", "SRI":"Spritzen", "SSU":"Sgl.-Suppositorien", "STA":"Stechampullen", "STB":"Stäbchen", "STI":"Stifte", "STR":"Streifen", "STY":"Styli", "SUB":"Substanz", "SUP":"Suppositorien", "SUS":"Suspension", "SUT":"Sublingualtabletten", "SWA":"Schwämme", "TAB":"Tabletten", "TAE":"Täfelchen", "TAM":"Trockenampullen", "TEE":"Tee", "TES":"Test", "TIN":"Tinktur", "TKA":"Tabletten in Kalenderpackung", "TLO":"Trinklösung", "TMR":"Tabletten magensaftresistent", "TON":"Tonikum", "TPN":"Tampon", "TPO":"Tamponaden", "TRA":"Trinkampullen", "TRG":"Trinkgranulat", "TRI":"Trituration", "TRL":"Tropflösung", "TRO":"Tropfen", "TRS":"Trockensubstanz mit Lösungsmittel", "TRT":"Trinktabletten", "TSA":"Trockensaft", "TSP":"Trockenspray", "TSS":"Trockensubstanz ohne Lösungsmittel", "TST":"Teststäbchen", "TTA":"Teetabletten", "TTB":"Testtabletten", "TTF":"Tee: tassenfertig", "TTR":"Teststreifen", "TTS":"Teststempel", "TUB":"Tube", "TUE":"Tücher", "TUP":"Tupfer", "UPA":"Umschlagpaste", "UTA":"Überzogene Tabletten", "VAL":"Vaginallösung", "VAR":"Vaginalring", "VAS":"Vaginalschaum", "VCR":"Vaginalcreme", "VDU":"Vaginaldusche", "VER":"Verband", "VGE":"Vaginalgel", "VKA":"Vaginalkapseln", "VKO":"Vaginalkonzentrat", "VLI":"Vlies", "VOV":"Vaginalovula", "VSA":"Vaginalsalbe", "VSP":"Vaginalspray", "VST":"Vaginalstäbchen", "VSU":"Vaginalsuppositorien", "VTA":"Vaginaltabletten", "WAG":"Waschgel", "WAT":"Watte", "WGA":"Wundgaze", "WUE":"Würfel", "XDG":"Duschgel", "XDS":"Deo-Spray", "XFC":"Feuchtigkeitscreme", "XFE":"Festiger", "XGE":"Gesichtsmilch", "XGM":"Gesichtsmaske", "XHA":"Halsband", "XHB":"Haarbalsam", "XHK":"Haarkur", "XHS":"Haarspülung", "XKL":"Körperlotion", "XLS":"Lippenstift", "XMU":"Make up", "XNC":"Nachtcreme", "XPB":"Pflegebalsam", "XPK":"Körperpflege", "XRA":"Rasierschaum", "XSB":"Schaumbad", "XSG":"Sonnenschutzgel", "XSS":"Sonnenschutzcreme", "XTC":"Tagescreme", "ZAM":"Zylinderampullen", "ZBU":"Zahnbürste", "ZCR":"Zahncreme", "ZGE":"Zahngel", "ZKA":"Zerbeißkapseln", "ZPA":"Zahnpasta" }

    id = models.IntegerField(primary_key=True) 
    tekstovi = models.ManyToManyField(Fertigarzneimitteltext, null=True, blank=True, related_name='abda_artikli')
    deutschfl = models.BooleanField(db_column='DeutschFl', default=0) 
    sortierung = models.IntegerField(null=True, db_column='Sortierung', blank=True, db_index=True) 
    produktname = models.CharField(max_length=95, db_column='Produktname', blank=True) 
    suchbegriff = models.CharField(max_length=95, db_column='Suchbegriff', blank=True, db_index=True) 
    produktgruppe = models.IntegerField(null=True, db_column='Produktgruppe', blank=True) 
    erfasstam = models.IntegerField(null=True, db_column='ErfasstAm', blank=True) 
    zusammensetzunggeprueftam = models.IntegerField(null=True, db_column='ZusammensetzungGeprueftAm', blank=True) 
    fertigarzneimittelanbieternr = models.IntegerField(null=True, db_column='FertigarzneimittelanbieterNr', blank=True) 
    mitvertriebanbieternr = models.IntegerField(null=True, db_column='MitvertriebAnbieterNr', blank=True) 
    atccode = models.CharField(max_length=42, db_column='AtcCode', blank=True, db_index=True) 
    fertigarzneimitteldrf = models.CharField(max_length=18, db_column='FertigarzneimittelDrf', blank=True, db_index=True) 
    verkehrsstatus = models.IntegerField(null=True, db_column='Verkehrsstatus', blank=True) 
    emeazulassungfl = models.BooleanField(db_column='EmeaZulassungFl', default=0) 
    monopraeparatfl = models.BooleanField(db_column='MonopraeparatFl', default=0) 
    veterinaerpraeparatfl = models.BooleanField(db_column='VeterinaerpraeparatFl', default=0) 
    dossierfl = models.BooleanField(default=0, db_column='DossierFl') 
    hilfsstoffebearbeitetfl = models.BooleanField(default=0, db_column='HilfsstoffeBearbeitetFl') 
    patientenhinweisfl = models.BooleanField(default=0, db_column='PatientenhinweisFl') 
    sonstigertextfl = models.BooleanField(default=0, db_column='SonstigerTextFl') 
    wirkstoffanzahl = models.IntegerField(null=True, db_column='Wirkstoffanzahl', blank=True) 
    wirkstoffnr = models.IntegerField(null=True, db_column='WirkstoffNr', blank=True) 
    wirkstoffdeutschfl = models.BooleanField(default=0, db_column='WirkstoffDeutschFl') 
    wirkstoffinternationalfl = models.BooleanField(default=0, db_column='WirkstoffInternationalFl') 
    wirkstoffdrfnr = models.IntegerField(null=True, db_column='WirkstoffDrfNr', blank=True) 
    wirkstoffdrfdeutschfl = models.BooleanField(default=0, db_column='WirkstoffDrfDeutschFl') 
    wirkstoffdrfinternationalfl = models.BooleanField(default=0, db_column='WirkstoffDrfInternationalFl') 
    wirkstoffmengenr = models.IntegerField(null=True, db_column='WirkstoffMengeNr', blank=True) 
    wirkstoffmengedeutschfl = models.BooleanField(default=0, db_column='WirkstoffMengeDeutschFl') 
    wirkstoffmengeinternationalfl = models.BooleanField(default=0, db_column='WirkstoffMengeInternationalFl') 
    wirkstoffmengedrfnr = models.IntegerField(null=True, db_column='WirkstoffMengeDrfNr', blank=True) 
    wirkstoffmengedrfdeutschfl = models.BooleanField(default=0, db_column='WirkstoffMengeDrfDeutschFl') 
    wirkstoffmengedrfinternationalfl = models.BooleanField(default=0, db_column='WirkstoffMengeDrfInternationalFl') 

    anbieter = models.ForeignKey(FamAnbieter, null=True, blank=True, related_name='abda_lijekovi')

    class Meta:
        db_table = u'abda_Fertigarzneimittel'
  
    def popis_djelatnih_tvari(self):
      return "<br/>\n".join([i.stoff.nazivi.get(vorzugsbezeichnungfl=1).name for i in self.sastav.filter(stofftyp=1, entsprichtstofffl=0).select_related()])

    def lista_djelatnih_tvari(self):
      return [i.stoff for i in self.sastav.filter(stofftyp=1, entsprichtstofffl=0).select_related()]

    def get_drf(self):
      try: return self.drflookup[self.fertigarzneimitteldrf]
      except: return self.fertigarzneimitteldrf
        
class SastavLijeka(models.Model):
  lijek = models.ForeignKey(Fertigarzneimittel, null=True, blank=True, related_name='sastav')
  komponentenr = models.IntegerField(null=True, db_column='KomponenteNr', blank=True)
  rangnr = models.IntegerField(null=True, db_column='RangNr', blank=True)
  stoff = models.ForeignKey(Stoff, related_name='lijekovi')
  suffix = models.CharField(max_length=720, db_column='Suffix', blank=True)
  stofftyp = models.IntegerField(null=True, db_column='Stofftyp', blank=True) 
  entsprichtstofffl = models.BooleanField(default=0, db_column='EntsprichtstoffFl')
  menge = models.CharField(max_length=120, db_column='Menge', blank=True)
  einheit = models.CharField(max_length=60, db_column='Einheit', blank=True)



  class Meta:
    db_table = u'abda_Fertigarzneimittelinhaltsstoff'

  def tip_tvari(self):
    if self.stofftyp == 1: return 'Djelatna tvar'
    else: return 'Pomoćna tvar'
  
  def naziv_tvari(self):
    try: return self.stoff.nazivi.get(vorzugsbezeichnungfl=1).name
    except: pass
  


class Tip_Pakiranja(models.Model):
  kratica = models.CharField(max_length = 5)
  naziv = models.CharField(max_length = 60)
  DATEGNorm = models.CharField(max_length = 5)

class Identifikacija_Boje(models.Model):
  naziv = models.CharField(max_length = 40)

class Identifikacija_Tip(models.Model):
  naziv = models.CharField(max_length = 80)

class Identifikacija(models.Model):
  SortNr = models.IntegerField()  
  FotoNr = models.CharField(max_length = 12)
  FormNr = models.IntegerField()  
  boja = models.ForeignKey(Identifikacija_Boje, related_name='identifikacija', null=True)
  tip = models.ForeignKey(Identifikacija_Tip, related_name='identifikacija', null=True)

  D = models.FloatField()
  H = models.FloatField()
  L = models.FloatField()
  B = models.FloatField()
  G = models.IntegerField()
  
  PraegV = models.CharField(max_length=40, null=True)
  PraegR = models.CharField(max_length=40, null=True)

  EigenFl = models.BooleanField() 
  Merkmale = models.CharField(max_length = 255, null=True)

  def fotka(self):
    return self.FotoNr.strip() + '.bmp'
 
  def poledina(self):
    import re
    if 'LOGO' in self.PraegR:
      re.sub(r'LOGO\{[0-9]*\}', '<img src=\{\{STATIC_URL\}\}\/\/static\/img\/identa/$1.jpg \/>', self.PraegR)
      return self.PraegR
    else: return self.PraegR

class Dobavljac(models.Model): 
  TIP_DOBAVLJACA = {
    1: "Produzent = Original-Hersteller",
    2: "Generika-Hersteller",
    3: "Reimporteur",
    4: "Importeur",
    5: "Großhändler",
    6: "Vertreiber",
    7: "Buchhändler",
    8: "Apotheke",
    9: "Rohstofflieferant",
    55: "Einkaufs-Pool",
    60: "Direktbestell-Provider",
    80: "Anb.m. Produktinfo (Text/Bild)",
    81: "Anb.m. Produktinfo (Text)",
    99: "Warenwirtschaft-Pool"}  

  id = models.IntegerField(primary_key=True) 
  naziv = models.CharField(max_length = 50)
  dodatak_nazivu = models.CharField(max_length = 40, null=True, blank=True)
  slug = models.CharField(max_length = 20, null=True, blank=True)
  kratica = models.CharField(max_length = 15, null=True, blank=True)
  etiketa = models.CharField(max_length = 15, null=True, blank=True)
  bbn = models.BigIntegerField(blank=True, null=True)
  iln = models.BigIntegerField(blank=True, null=True)
  tip = models.IntegerField(blank=True, null=True)
  ima_logo = models.BooleanField()

  def __unicode__(self): return "%s" % (self.naziv)

  class Meta: 
    verbose_name_plural = 'Dobavljaci'

  def fotka(self):
    return '/static/img/identa/dobavljac-' + str(self.id) + '.jpg'

  def tip_naziv(self):
    try: return self.TIP_DOBAVLJACA[self.tip]
    except: pass


def artikal_calc_maloprodajna_cijena(ApoEk, ApoVk, atc_id=None, apokz=0):
    import project.settings
    # pdv = project.settings.TaxRate
    def_pdv = settings.TaxRate
    apokz_pdv = settings.ApoKzTaxRate
    if 1 == apokz:
        pdv = apokz_pdv
    else:
        pdv = get_pdv(atc_id=atc_id)
    #marza = 0.017 * 1.1  # dignuo sam originalni koeficijent marze za 10%
    marza = 0.018  # dignuo sam originalni koeficijent marze za 10%
    k = marza * (pdv / 100.0 + 1.0)
    pdv_factor = (pdv + 100.0) / 10000.0
    if pdv < (def_pdv * 0.99):
        pdv_factor *= 1.1
        k *= 1.1
    if k * float(ApoEk) < pdv_factor * float(ApoVk):
        res = pdv_factor * float(ApoVk)
    else:
        res = k * float(ApoEk)
    return res


def artikal_calc_veleprodajna_cijena(ApoEk, ApoVk):
    #k = 0.017 * 1.1  # dignuo sam originalni koeficijent marze za 10%
    k = 0.018  # dignuo sam originalni koeficijent marze za 10%
    if k * float(ApoEk) < 0.01 * float(ApoVk):
        res = 0.01 * float(ApoVk)
    else:
        res = k * float(ApoEk)
    return res


class Artikal(models.Model, AdminSetter):
  abda_artikal = models.ForeignKey(Fertigarzneimittel, null=True, blank=True)

  aktivna_tvar = models.ForeignKey(Stoff, null=True, blank=True)
  
  Sortname1 = models.CharField(max_length=50, db_index=True)
  Sortname2 = models.CharField(max_length=50, db_index=True)

  NrKz = models.CharField(max_length=2)
  ZoNr = models.BigIntegerField(db_index=True)
  name = models.CharField(max_length=50, db_index=True)
  slug = models.CharField(max_length=50, db_index=True)

  kolicina = models.CharField(max_length=8)
  jedinice = models.CharField(max_length=8)
  std_kolicina = models.CharField(max_length=25)

  dobavljac = models.ForeignKey(Dobavljac, related_name='artikli', null=True) 
  pakiranje = models.ForeignKey(Tip_Pakiranja, related_name='artikli', null=True)
  identifikacija = models.ForeignKey(Identifikacija, related_name='artikli', null=True)
  ATC = models.ForeignKey(AtcCode, related_name='artikli', null=True)

  kratica_dobavljaca = models.CharField(max_length=10)

  stanje = models.PositiveIntegerField(null=True)

  ApoEk = models.IntegerField()
  ApoVk = models.IntegerField()
  KvaEk = models.IntegerField()
  HerVk = models.IntegerField()

  ApoKz = models.IntegerField(blank=True, null=True)

  cijena = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

  MehrKosten = models.BigIntegerField(null=True)
  KkRabattKz = models.IntegerField(null=True)
  HerRabatt = models.BigIntegerField(null=True)
  
  WarenGrp = models.CharField(max_length = 8)
  ATCCode = models.CharField(max_length = 7, db_index=True) 
  
  WirkstNr = models.BigIntegerField(null=True, db_index=True)
  WirkstMengeNr = models.BigIntegerField(null=True, db_index=True)
  AutIdemNr = models.BigIntegerField(null=True, db_index=True)
  AutIdemAbdaNr = models.BigIntegerField(null=True, db_index=True)
  AutSimile = models.BigIntegerField(null=True, db_index=True)
  PznOrg = models.BigIntegerField(null=True)
  
  M2Nr = models.BigIntegerField(null=True, db_index=True)

  MinBestell = models.IntegerField(null=True)
  VerpackungKz = models.IntegerField(null=True)
  
  

  RedInhFl = models.BooleanField(default=0)
  HilfsTaxFl = models.BooleanField(default=0)
  HtPreisFl = models.BooleanField(default=0)
  VeterinaerFl = models.BooleanField(default=0, db_index=True) 
  KleinPckFl = models.BooleanField(default=0) 
  BtmFl = models.BooleanField(default=0)
  WarnFl = models.BooleanField(default=0)
  VglHumanFl = models.BooleanField(default=0) 
  VglVetFl = models.BooleanField(default=0) 
  VdbFl = models.BooleanField(default=0)
  IdentaFl = models.BooleanField(default=0) 
  NachfolgerFl = models.BooleanField(default=0) 
  VorgaengerFl = models.BooleanField(default=0) 
  ZzFreiFl = models.BooleanField(default=0)
  EigenArtFl = models.BooleanField(default=0) 
  FdmFl = models.BooleanField(default=0) 
  WsFl = models.BooleanField(default=0)
  RlFl = models.BooleanField(default=0)
  KombiFl = models.BooleanField(default=0)
  MGDAFl = models.BooleanField(default=0)
  AmProfileFl = models.BooleanField(default=0)
  AdProfileFl = models.BooleanField(default=0)
  BerattetextFl = models.BooleanField(default=0) 
  IstAngebotVorhandenFl = models.BooleanField(default=0) 
  IstMarkAngebotVorhandenFl = models.BooleanField(default=0) 
  TfgFl = models.BooleanField(default=0)
  ZeitschriftFl = models.BooleanField(default=0)
  EigenerBeratungstextFl = models.BooleanField(default=0) 
  ProduktinfoFl = models.BooleanField(default=0)
  ZusatzverkaufFl = models.BooleanField(default=0)
  HkProfileFl = models.BooleanField(default=0)
  MehrkostenverzichtFl = models.BooleanField(default=0)
  Zuzahlungserlass = models.BooleanField(default=0)
  RabattvertragFl = models.BooleanField(default=0)
  BlisterfaehigFl = models.BooleanField(default=0)
  OralfestFl = models.BooleanField(default=0) 
  OralfluessigFl = models.BooleanField(default=0) 
  InvasivFl = models.BooleanField(default=0) 
  TeilbarkeitsinfoFl = models.BooleanField(default=0) 
  VerordnungsvorgabeFl = models.BooleanField(default=0) 
  TRezeptFl = models.BooleanField(default=0)
  SubstitutionshinweisFl = models.BooleanField(default=0)
  ParenteraliapreiseFl = models.BooleanField(default=0)
  BiotechFertigarzneimittelFl = models.BooleanField(default=0)
  SchuettwareFl = models.BooleanField(default=0)
  ProduktinfoAktuellFl = models.BooleanField(default=0)
  VerscheibungspflichtAusnahmeTextFl = models.BooleanField(default=0) 

  verkehrskz = models.IntegerField(default=0, db_column='verkehrskz')

  

  def __unicode__(self): return "%s" % (self.name)

  class Meta:
    verbose_name_plural = 'Artikli'
    ordering = ['Sortname1']

  def cijena_artikla(self):
    a = self.ApoEk
    return "%s.%s" % (str(a)[:-2], str(a)[-2:])
   
  def manipulativni(self):  
    a = self.ApoVk
    if a > 2050: return 600
    elif a > 550: return 400
    else: return 200
  
  
  
  def calc_maloprodajna_cijena(self):
    return artikal_calc_maloprodajna_cijena(self.ApoEk, self.ApoVk, self.ATC_id, self.ApoKz)

  def calc_veleprodajna_cijena(self):
    return artikal_calc_veleprodajna_cijena(self.ApoEk, self.ApoVk)

  def cijena_s_marzom(self):
    return "%.2f" % self.calc_maloprodajna_cijena()

  def cijena_s_marzom_vp(self):
    return "%.2f" % self.calc_veleprodajna_cijena()

  def ukupna_cijena(self):
    return self.cijena_s_marzom() + self.manipulativni()
  
  def lista_djelatnih_tvari(self):
    try: return SastavLijeka.objects.filter(lijek=self.WirkstNr, stofftyp=1).values_list('stoff_id', flat=True)
    except: pass
  
  def lista_djelatnih_tvari_obj(self):
    try: return SastavLijeka.objects.filter(lijek=self.WirkstNr, stofftyp=1).stoff.all()
    except: pass



class ArtikalSearch(forms.Form):
  dobavljac = forms.CharField(max_length=64, required=False)
  djelatna_tvar_1 = forms.CharField(max_length=64, required=False)
  djelatna_tvar_2 = forms.CharField(max_length=64, required=False)
  djelatna_tvar_3 = forms.CharField(max_length=64, required=False)
  pzn = forms.CharField(max_length=64, required=False)
  ean = forms.CharField(max_length=64, required=False)
  atc = forms.CharField(max_length=64, required=False)

 
class VrstaIzmjeneCijena(models.Model):
  aendergrp = models.IntegerField()
  erklaerung = models.CharField(max_length=40)
  tabellenid = models.IntegerField()
  feld = models.CharField(max_length=128)
  lookupthema = models.IntegerField()
  kurybezeichnung = models.BooleanField(default=False)  

class ArhivaCijena(models.Model):
  artikal = models.ForeignKey(Artikal, related_name='arhiva_cijena')
  sifra = models.ForeignKey(VrstaIzmjeneCijena, db_index=True)
  datoteka = models.IntegerField(db_index=True)

  prije_izmjene = models.CharField(max_length=50)
  nakon_izmjene = models.CharField(max_length=50)

  trend = models.IntegerField()

    
class Dimenzije(models.Model):
  artikal = models.OneToOneField(Artikal, null=True)
  duljina = models.IntegerField()
  sirina = models.IntegerField()
  visina = models.IntegerField()
  masa = models.IntegerField()
  
class EAN(models.Model):
  artikal = models.ForeignKey(Artikal, related_name='ean')
  kod = models.CharField(max_length=20, db_index=True)

class Dobavljac_Telefon(models.Model):
  TIP_TELEFONA = (
        (0, 'Odaberite tip'),
        (1, 'Telefon'),
        (2, 'Telefax'),
        (3, '??'),
        (4, 'E-Mail'),
        (5, 'Web site'),
  )
  dobavljac = models.ForeignKey(Dobavljac, related_name='telefoni')
  sortnr = models.IntegerField()
  telefonart = models.IntegerField() 
  broj = models.CharField(max_length=100)
  kontakt_osoba = models.CharField(max_length=100, null=True, blank=True)
  
  def telefon_human_readable(self):
    try: return self.TIP_TELEFONA[self.telefonart][1]
    except: pass

class Dobavljac_Tip_Adrese(models.Model):
  tip = models.CharField(max_length=6)
  opis = models.CharField(max_length=50, null=True, blank=True)
  upucivanje = models.BooleanField()

class Dobavljac_Adresa(models.Model):
  dobavljac = models.ForeignKey(Dobavljac, related_name='adrese')
  tip = models.ForeignKey(Dobavljac_Tip_Adrese, related_name='adrese')
  sortnr = models.IntegerField()
  distribucija = models.CharField(max_length=80)
  ulica = models.CharField(max_length=40, null=True, blank=True)
  postanski_broj = models.CharField(max_length=10, null=True, blank=True)
  mjesto = models.CharField(max_length=40, null=True, blank=True)
  kod_zemlje = models.CharField(max_length=4, null=True, blank=True)

  veleprodaja_postanski = models.CharField(max_length=10, null=True, blank=True)
  veleprodaja_mjesto = models.CharField(max_length=40, null=True, blank=True)
  
  po_box = models.CharField(max_length = 10, null=True, blank=True)
  po_box_postanski = models.CharField(max_length=10, null=True, blank=True)
  po_box_mjesto = models.CharField(max_length=40, null=True, blank=True)
  
  sort_grad = models.CharField(max_length=20, null=True, blank=True)

  def broj(self):
    try: return self.dobavljac.telefoni.filter(sortnr=self.sortnr)
    except: pass

class Dobavljac_Rabat(models.Model):
  TIP_RABATA = (
        (1, 'Rabatt für nicht festbetragsgebundene Arzneimittel gemäß § 130a SGB V Abs. 1'),
        (2, 'Rabatt für patentfreie, wirkstoffgleiche Arzneimittel gemäß § 130a SGB V Abs. 3b'),
        (3, 'Rabatt durch Preismoratorium gemäß § 130a SGB V Abs. 3a'),
        (4, 'Rabatt für Impfstoffe gemäß § 130a SGB V Abs. 2'),
        (5, 'Rabatt aufgrund Nutzenbewertung gemäß § 130b SGB V'),
  )
  artikal = models.ForeignKey(Artikal, related_name='rabati')
  iznos = models.BigIntegerField()
  tip = models.IntegerField(choices=TIP_RABATA)

class ListaHZZO(models.Model):
  ATC = models.ForeignKey(AtcCode, null=True, blank=True, related_name='listahzzo')
  ATC_naziv = models.CharField(max_length=20)
  genericko_ime = models.CharField(max_length=320, null=True, blank=True)
  ddd_jed_mj = models.CharField(max_length=40, null=True, blank=True)
  proizvodac = models.CharField(max_length=140, null=True, blank=True)
  zasticeno_ime_lijeka = models.CharField(max_length=270, null=True, blank=True)
  oblik_lijeka = models.CharField(max_length=500, null=True, blank=True)
  cijena_u_kn_za_jed_oblika = models.CharField(max_length=120, null=True, blank=True)
  cijena_u_kn_za_orig_pakir = models.CharField(max_length=120, null=True, blank=True)
  napomena = models.CharField(max_length=6000, null=True, blank=True)
  grupa = models.CharField(max_length=250, null=True, blank=True)
  podgrupa = models.CharField(max_length=250, null=True, blank=True)
  pdv = models.DecimalField(max_digits=12, decimal_places=2, null=True)
  

class ListaALMP(models.Model):
  ATC = models.ForeignKey(AtcCode, null=True, blank=True, related_name='listaalmp')
  rok_rjesenja = models.CharField(max_length=500, null=True, blank=True)
  datum_rjesenja = models.CharField(max_length=500, null=True, blank=True)
  urbroj = models.CharField(max_length=500, null=True, blank=True)
  nacin_propisivanja = models.CharField(max_length=500, null=True, blank=True)
  nacin_izdavanja = models.CharField(max_length=500, null=True, blank=True)
  klasa = models.CharField(max_length=500, null=True, blank=True)
  proizvodac = models.CharField(max_length=500, null=True, blank=True)
  atk = models.CharField(max_length=50, null=True, blank=True)
  nositelj_odobrenja = models.CharField(max_length=500, null=True, blank=True)
  pakovanje = models.CharField(max_length=1000, null=True, blank=True)
  farmaceutski_oblik = models.CharField(max_length=500, null=True, blank=True)
  uputa_o_lijeku = models.CharField(max_length=500, null=True, blank=True)
  djelatna_tvar = models.CharField(max_length=1000, null=True, blank=True)
  sastav = models.CharField(max_length=5000, null=True, blank=True)
  naziv = models.CharField(max_length=1000, null=True, blank=True)
  sazetak_opisa = models.CharField(max_length=5000, null=True, blank=True)
  nacin_oglasavanja = models.CharField(max_length=500, null=True, blank=True)
    
def get_pdv(atc_id=None, atc_sifra=None):
    res = settings.TaxRate
    if None == atc_id and None == atc_sifra:
        return res
    elif None == atc_id:
        try:
            atc_id = AtcCode.objects.filter(sifra=atc_sifra)[0].id
        except:
            # TODO: log error
            return res
    try:
        pdv = ListaHZZO.objects.filter(ATC_id=atc_id)[0].pdv
    except:
        # TODO: log error
        return res
    if None != pdv:
        res = float(pdv)
    return res

