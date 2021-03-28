#!/usr/bin/python

import os
import sys

sys.path.append(os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "/../"))

os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'


#--------------------------------------------------------------------------------------------------


def import_depo_csv():
    from project.depo.models import Lijek

    class CSVImportItem():
        pass

    def import_csv_report(fname):
        import csv
        report = []

        f  = open(fname, "rb")
        reader = csv.reader(f, dialect='excel-tab')

        rownum = 0
        for row in reader:
            # Save header row.
            if rownum == 0:
                header = row
            else:
                item = CSVImportItem()
                item.id = row[0]
                item.nabavna_cijena_eur = row[3].replace(",", ".")
                report.append(item)
            rownum += 1

        f.close()

        return report

    report = import_csv_report("/tmp/depo.csv")

    for r in report:
        Lijek.objects.filter(id=r.id).update(nabavna_cijena_eur=r.nabavna_cijena_eur)


#--------------------------------------------------------------------------------------------------


def rework_netherlands_article_codes():
    from project.order.models import ArtikalDrugoTrziste
    import csv
    import re

    """
    f = open("/tmp/NL.csv", "rb")
    reader = csv.reader(f, dialect='excel-tab')

    rownum = 0
    for row in reader:
        # skip header row.
        if rownum == 0:
            header = row
        else:
            sifra = row[0]
            ime = row[1]
            kolicina_jed = row[2]

            m = re.search(r"^([\d,]+x[\d,]+|[\d,]+)([a-zA-Z\s]+)", kolicina_jed)

            try:
                item = ArtikalDrugoTrziste.objects.get(trziste_id=4, ime__icontains=sifra)
                item.sifra = sifra
                item.kolicina_jed = kolicina_jed
                item.kolicina = m.group(1)
                item.jedinice = m.group(2)
                item.ime = item.ime.replace(sifra, "").strip()
                item.save()
            except:
                print "not found: ", ime

            if rownum % 100 == 0:
                print rownum

        rownum += 1

    f.close()
    """

    cnt = ArtikalDrugoTrziste.objects.filter(trziste_id=4).count()
    for n, item in enumerate(ArtikalDrugoTrziste.objects.filter(trziste_id=4)):
        s = re.sub(r" [G\-\d]+[a]?$", "", item.ime).strip()
        if item.ime != s:
            print "{:50}".format(item.ime), "->", s
            item.ime = s
            item.save()
        if n % 100 == 0:
            print "************************* %d / %d" % (n, cnt)


#--------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "rework_netherlands_article_codes":
            rework_netherlands_article_codes()
