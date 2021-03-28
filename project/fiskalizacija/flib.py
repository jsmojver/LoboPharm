#!/usr/bin/python

import sys, time, libxml2, xmlsec, os, StringIO, uuid, base64, hashlib, suds
from suds.client import Client
from suds.plugin import MessagePlugin, PluginContainer
from M2Crypto import RSA
import project.settings

######################
keyFile = '%s/fiskalizacija/doo-kljuc.pem' % (project.settings.local.ProjectPath)
certFile = '%s/fiskalizacija/doo-cert.pem' % (project.settings.local.ProjectPath)
verifyCertFile = '%s/fiskalizacija/cis_i_rdc.pem' % (project.settings.local.ProjectPath)

import logging

try:
    import flib_log
except:
    # Send log messages to console
    logging.basicConfig(level=logging.INFO, filename='/var/log/fiskalizacija.log')
    # Set Suds logging level to debug, outputs the SOAP messages.
    logging.getLogger('suds.client').setLevel(logging.DEBUG)
    logging.getLogger('suds.transport').setLevel(logging.DEBUG)


###################### Override failed metode zbog XML cvora koji fali u odgovoru porezne ################

def _failed(self, binding, error):
   status, reason = (error.httpcode, str(error))
   reply = error.fp.read()
   if status == 500:
      if len(reply) > 0:
         reply, result = binding.get_reply(self.method, reply)
         self.last_received(reply)
         plugins = PluginContainer(self.options.plugins)
         ctx = plugins.message.unmarshalled(reply=result)
         result = ctx.reply
         return (status, result)
      else:
         return (status, None)
   if self.options.faults:
      raise Exception((status, reason))
   else:
      return (status, None)

suds.client.SoapClient.failed = _failed

##########################################################################################################
def zkicalc(params):    
  """ Izracun ZKI po zelji, parametar je lista parametara za ZKI """
  return hashlib.md5(RSA.load_key(keyFile).sign(hashlib.sha1(''.join(map(str, params))).digest())).hexdigest()

#########################################################################################################

class DodajPotpis(MessagePlugin):
  def __init__(self): 
    self.poruka_odgovor = ''
    self.valid_signature = 0
 
  def sending(self, context):

    msgtype = "RacunZahtjev"
    if "PoslovniProstorZahtjev" in context.envelope: msgtype = "PoslovniProstorZahtjev"
    
    doc2 = libxml2.parseDoc(context.envelope)

    racunzahtjev = doc2.xpathEval('//*[local-name()="%s"]' % msgtype)[0]
    doc2.setRootElement(racunzahtjev)

    x = doc2.getRootElement().newNs('http://www.apis-it.hr/fin/2012/types/f73', 'tns')
 
    for i in doc2.xpathEval('//*'):
      i.setNs(x)

    libxml2.initParser()
    libxml2.substituteEntitiesDefault(1)

    xmlsec.init()
    xmlsec.cryptoAppInit(None)
    xmlsec.cryptoInit()

    doc2.getRootElement().setProp('Id', msgtype)
    xmlsec.addIDs(doc2, doc2.getRootElement(), ['Id'])    

    signNode = xmlsec.TmplSignature(doc2, xmlsec.transformExclC14NId(), xmlsec.transformRsaSha1Id(), None)

    doc2.getRootElement().addChild(signNode)
    
    refNode = signNode.addReference(xmlsec.transformSha1Id(), None, None, None)
    refNode.setProp('URI', '#%s' % msgtype)
    refNode.addTransform(xmlsec.transformEnvelopedId())
    refNode.addTransform(xmlsec.transformExclC14NId())
 
    dsig_ctx = xmlsec.DSigCtx()
    key = xmlsec.cryptoAppKeyLoad(keyFile, xmlsec.KeyDataFormatPem, None, None, None)
    dsig_ctx.signKey = key
    xmlsec.cryptoAppKeyCertLoad(key, certFile, xmlsec.KeyDataFormatPem)
    key.setName(keyFile)

    keyInfoNode = signNode.ensureKeyInfo(None)
    x509DataNode = keyInfoNode.addX509Data()
    xmlsec.addChild(x509DataNode, "X509IssuerSerial")
    xmlsec.addChild(x509DataNode, "X509Certificate")

    dsig_ctx.sign(signNode)
    
    if dsig_ctx is not None: dsig_ctx.destroy()
    context.envelope = """<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>""" + doc2.serialize().replace('<?xml version="1.0" encoding="UTF-8"?>','') + """</soapenv:Body></soapenv:Envelope>""" # Ugly hack
    
    # Shutdown xmlsec-crypto library, ako ne radi HTTPS onda ovo treba zakomentirati da ga ne ugasi prije reda
    xmlsec.cryptoShutdown()
    xmlsec.shutdown()
    libxml2.cleanupParser()

    return context

  def received(self, context):
    self.poruka_odgovor = context.reply

    libxml2.initParser()
    libxml2.substituteEntitiesDefault(1)

    xmlsec.init()
    xmlsec.cryptoAppInit(None)
    xmlsec.cryptoInit()

    mngr = xmlsec.KeysMngr()
    xmlsec.cryptoAppDefaultKeysMngrInit(mngr)
    mngr.certLoad(verifyCertFile, xmlsec.KeyDataFormatPem, xmlsec.KeyDataTypeTrusted)

    doc = libxml2.parseDoc(context.reply)
    xmlsec.addIDs(doc, doc.getRootElement(), ['Id'])
    node = xmlsec.findNode(doc.getRootElement(), xmlsec.NodeSignature, xmlsec.DSigNs)
    dsig_ctx = xmlsec.DSigCtx(mngr)
    dsig_ctx.verify(node)
    if(dsig_ctx.status == xmlsec.DSigStatusSucceeded): self.valid_signature = 1 

    xmlsec.cryptoShutdown()
    xmlsec.cryptoAppShutdown()
    xmlsec.shutdown()
    libxml2.cleanupParser()
    return context


############################################################################################################################################

class Fiskalizacija():
  wsdl = 'file://%s/fiskalizacija/wsdl/FiskalizacijaServiceProdukcijski.wsdl' % (project.settings.local.ProjectPath) # Za test

  potpisPlugin = DodajPotpis()

  client_ping = Client(wsdl, cache=None, prettyxml=True, timeout=5, faults=False) 
  #client2 = Client(wsdl, prettyxml=True, timeout=3, faults=False, plugins=[DodajPotpis()]) 
  client2 = Client(wsdl, cache=None, prettyxml=True, timeout=5, faults=False, plugins=[potpisPlugin]) 
  client2.add_prefix('tns', 'http://www.apis-it.hr/fin/2012/types/f73')

  client_ping.set_options(headers={'User-agent': 'FiskalnaBlagajna/v1.0 (GNU/Linux)'})
  client2.set_options(headers={'User-agent': 'FiskalnaBlagajna/v1.0 (GNU/Linux)'})
 
  def __init__(self): 
    self.racun = self.client2.factory.create('tns:Racun')
    self.zaglavlje = self.client2.factory.create('tns:Zaglavlje')

  def izracunaj_zastitni_kod(self, datumvrijeme):    
    medjurezultat = self.racun.Oib + str(datumvrijeme) + str(self.racun.BrRac.BrOznRac) + self.racun.BrRac.OznPosPr + self.racun.BrRac.OznNapUr + str(self.racun.IznosUkupno)
    pkey = RSA.load_key(keyFile)
    signature = pkey.sign(hashlib.sha1(medjurezultat).digest())
    self.racun.ZastKod = hashlib.md5(signature).hexdigest()

  def posalji(self):
    return self.client2.service.racuni(self.zaglavlje, self.racun)

  def generiraj_poruku(self):
    self.client2.options.nosend = True
    poruka = str(self.client2.service.racuni(self.zaglavlje, self.racun).envelope)
    self.client2.options.nosend = False
    return poruka
  
  def echo(self):
    self.echo_response = self.client_ping.service.echo('ping')



