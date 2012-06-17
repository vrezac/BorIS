from django.conf.urls.defaults import url, patterns
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.template.defaultfilters import slugify
from django.utils.functional import update_wrapper

from boris.reporting.core import ReportResponse
from boris.reporting.forms import MonthlyStatsForm, ServiceForm
from boris.reporting.reports.monthly_stats import MonthlyStatsByTown, \
    MonthlyStatsByDistrict
from boris.reporting.reports.yearly_stats import YearlyStatsByMonth
from boris.reporting.reports.services import ServiceReport

class ReportingInterfaceTab(object):
    """
    One tab of the interface. Requires 2 attributes to be set:
        `report`       Report subclass
        `form`         Form used to get parameters for report initiation
    """
    report = None
    form = None

    @classmethod
    def get_urlname(cls):
        return 'reporting_%s' % cls.__name__.lower()

    def get_title(self):
        return self.report.title

    def get_description(self):
        return self.report.description

    def get_absolute_url(self):
        return reverse(self.get_urlname())


def interfacetab_factory(ReportClass, FormClass):
    return type(ReportClass.__name__ + 'Tab', (ReportingInterfaceTab,), {
        'report': ReportClass, 'form': FormClass})

class ReportingInterface(object):
    """
    Separate report forms are splitted to tabs in admin, this
    class handles management of these forms.

    Tabs are defined as ReportInterfaceTab subclasses listed in
    `tabs` attribute.
    """
    tabs = (
        interfacetab_factory(MonthlyStatsByTown, MonthlyStatsForm),
        interfacetab_factory(MonthlyStatsByDistrict, MonthlyStatsForm),
        interfacetab_factory(YearlyStatsByMonth, MonthlyStatsForm),
        interfacetab_factory(ServiceReport, ServiceForm)
    )


class ReportingInterfaceHandler(object):
    """Class-based view for showing reporting interface."""

    def __call__(self, request, tab_class=None):
        interface = ReportingInterface()
        tabs = {}

        for t in interface.tabs:
            tab = t()
            if tab_class == t and request.method == 'POST':
                form = tab.form(request.POST)
                if form.is_valid():
                    return ReportResponse(tab.report, **form.cleaned_data)
            else:
                form = tab.form()
            tabs[tab] = form

        ctx = {'tabs': sorted(tabs.items()), 'interface': interface}
        return render(request, 'reporting/interface.html', ctx)

    def get_urls(self):
        """
        Returns all urls for interface. Each tab has it's own POST URL plus
        there is one extra URL for base view.
        """

        interface = ReportingInterface()

        urlpatterns = patterns('',
            url('^$', admin.site.admin_view(self.__call__, cacheable=True),
                name='reporting_base')
        )

        for t in interface.tabs:
            urlpatterns += patterns('',
                url(r'^%s/$' % slugify(t.__name__), admin.site.admin_view(
                            self.__call__, cacheable=False),
                    kwargs={'tab_class': t}, name=t.get_urlname())
            )

        return urlpatterns, 'reporting', None
    urls = property(get_urls)

interface = ReportingInterfaceHandler()

