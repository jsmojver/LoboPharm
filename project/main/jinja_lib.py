# -*- coding: utf-8 -*-

from coffin import template
from coffin.shortcuts import render_to_string
from coffin.template import RequestContext
import project.settings


#--------------------------------------------------------------------------------------------------


def slugify(text):
    from django.template.defaultfilters import slugify
    return slugify(text)


#--------------------------------------------------------------------------------------------------


def format_float(value, precision=2, group_digits=True):
    res = "0"
    try:
        if precision != None:
            precison_str = "%%.%df" % precision
            res = (precison_str % value).replace(".", ",")
        else:
            res = ("%g" % value).replace(".", ",")
    except:
        pass

    if group_digits:
        a = res.split(",")
        dec = a[0]
        frac = a[1] if len(a) > 1 else ""

        if len(dec) > 0 and dec[0] == "-":
            neg = True
            dec = dec[1:]
        else:
            neg = False

        if len(dec) > 3:
            g = []
            while len(dec) > 0:
                g.append(dec[-3:])
                dec = dec[:len(dec)-3] if len(dec) > 3 else ""
            dec = ".".join(reversed(g))

        res = "%s,%s" % (dec, frac) if len(frac) != 0 else dec
        if neg:
            res = "-%s" % (res)

    return res


#--------------------------------------------------------------------------------------------------


def format_float_thousands(value, precision=0):
    import locale
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

    try:
        if precision != 0:
            precison_str = "%%.%df" % precision
            return locale.format(precison_str, value, True)
        else:
            return locale.format("%d", value, True)
    except:
        return "0"


#--------------------------------------------------------------------------------------------------


def format_datetime(value, format="%d.%m.%Y %H:%M", include_seconds=False):
    try:
        if include_seconds:
            format="%d.%m.%Y %H:%M:%S"
        return value.strftime(format)
    except (AttributeError, ValueError):
        return "-"


#--------------------------------------------------------------------------------------------------


def format_date(value, format="%d.%m.%Y"):
    return format_datetime(value, format=format)


#--------------------------------------------------------------------------------------------------


def format_time(value, format="%H:%M"):
    return format_datetime(value, format=format)

#--------------------------------------------------------------------------------------------------


def format_weekday(value):
    from django.utils.translation import ugettext as _
    try:
        return [_("Nedjelja"), _("Ponedjeljak"), _("Utorak"), _("Srijeda"), _(u"Četvrtak"), _("Petak"), _("Subota")][int(value.strftime("%w"))]
    except (AttributeError, ValueError):
        return "-"


#--------------------------------------------------------------------------------------------------


def format_weekday_date(value):
    return "%s, %s" % (format_weekday(value), format_date(value))


#--------------------------------------------------------------------------------------------------


def format_currency(value):
    return '{:,.2f}'.format(value)


#--------------------------------------------------------------------------------------------------


def format_filesize(value):

    try:
        value = int(value)
    except:
        value = 0

    if value < 1024:
        return "1 kB"

    for x in ['bytes', 'kB', 'MB', 'GB', 'TB']:
        if value < 1024.0:
            return "%3.1f %s" % (value, x)
        value /= 1024.0


#--------------------------------------------------------------------------------------------------


def ago(d):
    import datetime
    now = datetime.datetime.now()

    # ignore microsecond part of 'd' since we removed it from 'now'
    delta = now - (d - datetime.timedelta(0, 0, d.microsecond))

    if delta.days < 7:
        chunks = (
          (60 * 60 * 24 * 365, 'y'),
          (60 * 60 * 24 * 30, 'm'),
          (60 * 60 * 24 * 7, 'w'),
          (60 * 60 * 24, 'd'),
          (60 * 60, 'h'),
          (60, 'min')
        )

        since = delta.days * 24 * 60 * 60 + delta.seconds
        if since <= 0:
            # d is in the future compared to now, stop processing.
            return u'0 ' + 'min ago'
        for i, (seconds, name) in enumerate(chunks):
            count = since // seconds
            if count != 0:
                break
        s = '%(number)d %(type)s' % {'number': count, 'type': name}
        if i + 1 < len(chunks):
            # Now get the second item
            seconds2, name2 = chunks[i + 1]
            count2 = (since - (seconds * count)) // seconds2
            if count2 != 0:
                s += ', %(number)d %(type)s' % {'number': count2, 'type': name2}

        return "prije %s" % s
    else:
        return d.strftime("%d.%m.%Y")


#--------------------------------------------------------------------------------------------------


import re
from jinja2 import evalcontextfilter, Markup, escape
_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')


@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br/>\n') \
        for p in _paragraph_re.split(value))
    if eval_ctx is not None and eval_ctx.autoescape:
        result = Markup(result)
    return result


#--------------------------------------------------------------------------------------------------


def manytomany_to_id_str_list(obj):
    if obj:
        return ",".join(["%d" % item.id for item in obj])
    else:
        return ""


#--------------------------------------------------------------------------------------------------


def push(array, value):
    array.append(value)
    return array


#--------------------------------------------------------------------------------------------------


def lipsum(words=None, paragraphs=None):
    from django.contrib.webdesign import lorem_ipsum
    if words is not None:
        return lorem_ipsum.words(words)
    elif paragraphs is not None:
        res = []
        for line in lorem_ipsum.paragraphs(paragraphs):
            res.append("<p>%s</p>" % (line))
        return "\n".join(res)
    else:
        return ""

#--------------------------------------------------------------------------------------------------


JINJA2_GLOBALS = {
    "get_site_name": lambda: project.settings.local.SiteName,
    "get_header_copyright": lambda: project.settings.local.HeaderCopyright,
    "get_header_author": lambda: project.settings.local.HeaderAuthor,
    "is_paymentgateway_debug": lambda: project.settings.local.PaymentGatewayDebug,
    "using_ie_printing_control": lambda: project.settings.local.USE_IE_PRINTING_CONTROL,
    "slugify": slugify,
    "format_datetime": format_datetime,
    "len": lambda value: len(value),
    "push": push,
    "get_css_fonts_path": lambda: project.settings.local.PDFFontsPath,
    "get_site_url": lambda: project.settings.local.SiteURL,
    "lipsum": lipsum,
}
project.settings.JINJA2_GLOBALS.update(JINJA2_GLOBALS)
