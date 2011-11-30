'''
Created on 20.11.2011

@author: xaralis
'''
from collections import defaultdict

from django.http import HttpResponse
from django.template import loader


class hashdict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class ReportResponse(HttpResponse):
    """
    Ancestor of HttpRespose which takes report class and its args and kwargs
    that renders itself.
    """
    def __init__(self, report_class, *args, **kwargs):
        report = report_class(*args, **kwargs)
        super(ReportResponse, self).__init__(content=report.render(), mimetype=report.mime)
        self['Content-Disposition'] = 'attachment; filename=report.csv'


class Column(object):
    def __init__(self, key, title=None):
        self.key = key
        if title is None:
            self.title = unicode(self.key)
        else:
            self.title = title

    def __unicode__(self):
        return  self.title

    def get_key(self):
        return self.key


class Row(object):
    def __init__(self, report, title=None):
        self.report = report
        if title is not None:
            self.title = title

    def __unicode__(self):
        return unicode(self.title)

    def get_val(self, column):
        """
        Returns value of cell for current row and given column.
        """
        return NotImplementedError


class Report(object):
    """
    Base class for reporting output. It's supposed to act as table so it
    has dynamically generated columns and rows based on queryset.

    When using with AggregationRows, subclasses might (or must) specify
    the following attributes:

    - grouping (required)
    - additional_filtering (optional)
    - additional_excludes (optional)
    """
    title = None
    columns = None
    rows = None
    row_classes = ()
    column_keys = ()

    def __unicode__(self):
        return self.title

    @property
    def mime(self):
        return 'application/vnd.ms-excel'

    @property
    def template(self):
        return (
            'reporting/reports/%s.html' % self.__class__.__name__.lower(),
            'reporting/reports/default.html'
        )

    def get_context(self):
        return {'report': self}

    def render(self):
        return loader.render_to_string(self.template, self.get_context())

    @property
    def columns(self):
        if not hasattr(self, '_columns'):
            self._columns = [Column(key, title=self.column_title(key))
                for key in self.column_keys]
        return self._columns

    def column_title(self, key):
        return unicode(key)

    @property
    def rows(self):
        if not hasattr(self, '_rows'):
            self._rows = [RowClass(self) for RowClass in self.row_classes]
        return self._rows


class AggregationRow(Row):
    """
    Main reporting logic lives in AggregationRow. It does aggregation
    on queryset specified by report.

    Subclasses can supply filtering/excluding, grouping and column, which
    should be treated as distinct (the one to report on).
    """
    filtering = {}
    excludes = {}
    aggregation_dbcol = 'id'
    model = None

    def __init__(self, *args, **kwargs):
        super(AggregationRow, self).__init__(*args, **kwargs)
        if hasattr(self.report, 'additional_filtering'):
            self.filtering.update(self.report.additional_filtering)
        if hasattr(self.report, 'additional_excludes'):
            self.excludes.update(self.report.additional_excludes)
        self.grouping = self.report.grouping

    def _values(self):
        if not hasattr(self, '__values'):
            qset = self.model.objects.all()

            if self.filtering:
                qset = qset.filter(**self.filtering)

            if self.excludes:
                qset = qset.exclude(**self.excludes)

            self.__values = defaultdict(int)
            vals = qset.values(*self.grouping).order_by().annotate(
                    total=self._annotation_func())

            for value in vals:
                key = hashdict((k, value[k]) for k in self.grouping)
                self.__values[key] += value['total']

        return self.__values

    def _annotation_func(self):
        """
        Function to create reporting on. Defaults to COUNT.
        """
        from django.db.models import Count
        return Count(self.aggregation_dbcol, distinct=True)

    def itervalues(self):
        """
        Iterate over values for all columns in report.
        """
        for column in self.report.columns:
            yield self.get_val(column)

    def get_val(self, column):
        """
        Return value for given column.
        """
        return self._values()[column.get_key()]

class SumAggregationRow(AggregationRow):
    """
    Row that uses SUM instead of COUNT to aggregate.
    """
    def _annotation_func(self):
        from django.db.models import Sum
        return Sum(self.aggregation_dbcol)
