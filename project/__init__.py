from django.core.paginator import Paginator, Page
from django.template.loader import add_to_builtins

add_to_builtins('project.order.templatetags.mytagslib')

class PageMixin :
    def digg_page_range(self) :
        page = self
	paginator = self.paginator

        BODY_PAGES = 5
        MARGIN_PAGES = 2
        TAIL_PAGES = 2

        position = 1

        p, q = TAIL_PAGES, max(1, min(page.number - BODY_PAGES / 2, paginator.num_pages - BODY_PAGES + 1))

        if q - p > MARGIN_PAGES :
            for x in xrange(position, p + 1) :
                yield x

            yield None

            position = q

        p, q = q + BODY_PAGES - 1, paginator.num_pages - TAIL_PAGES + 1

        if q - p > MARGIN_PAGES :
            for x in xrange(position, p + 1) :
                yield x

            yield None

            position = q

        for x in xrange(position, paginator.num_pages + 1) :
            yield x

if PageMixin not in Page.__bases__ :
    Page.__bases__ = (PageMixin,) + Page.__bases__

