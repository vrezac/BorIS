# -*- coding: utf-8 -*-
'''
Created on 2.10.2011

@author: xaralis
'''
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .core import ClientService

class HarmReduction(ClientService):
    in_count = models.PositiveSmallIntegerField(default=0, verbose_name=_(u'IN'))
    out_count = models.PositiveSmallIntegerField(default=0, verbose_name=_(u'OUT'))
    
    sterilized_water = models.BooleanField(default=False,
        verbose_name=_(u'sterilizovaná voda'))
    cotton_filters = models.BooleanField(default=False,
        verbose_name=_(u'bavlněné filtry'))
    alcohol_swabs = models.BooleanField(default=False,
        verbose_name=_(u'alkoholové tampony'))
    acid = models.BooleanField(default=False, verbose_name=_(u'kyselina'))
    alu_foil = models.BooleanField(default=False, verbose_name=_(u'alobal'))
    condoms = models.BooleanField(default=False, verbose_name=_(u'kondomy'))
    jelly_capsules = models.BooleanField(default=False,
        verbose_name=_(u'želatinové kapsle'))
    stericup = models.BooleanField(default=False, verbose_name=_(u'stéricup'))
    other = models.BooleanField(default=False, verbose_name=_(u'jiné'))
    
    pregnancy_test = models.BooleanField(default=False, verbose_name=_(u'těhotenský test'))
    medical_supplies = models.BooleanField(default=False, verbose_name=_(
        u'zdravotnický materiál'), help_text=_(u'náplasti, buničina, vitamíny, '
        '...'))

    class Meta:
        app_label = 'services'
        verbose_name = _(u'Harm Reduction')
        verbose_name_plural = _(u'Harm Reduction')
        
    class Service:
        title = _(u'Výměnný a jiný harm reduction program')
        fieldsets = (
            (None, {'fields': ('in_count', 'out_count', 'encounter'),
                'classes': ('inline',)}),
            (_(u'Harm Reduction'), {'fields': (
                'sterilized_water', 'cotton_filters', 'alcohol_swabs', 'acid',
                'alu_foil', 'condoms', 'jelly_capsules', 'stericup', 'other',
            ), 'classes': ('inline',)}),
            (_(u'Ostatní'), {'fields': ('pregnancy_test', 'medical_supplies'),
                'classes': ('inline',)})
        )
        

class AsistService(ClientService):
    where = models.CharField(max_length=255, verbose_name=_(u'Kam'))
    note = models.TextField(null=True, blank=True, verbose_name=_(u'Poznámka'))
    
    class Meta:
        app_label = 'services'
        verbose_name = _(u'Asistenční služba')
        verbose_name_plural = _(u'Asistenční služby')
        
    def _prepare_title(self):
        return _(u'%(title)s: doprovod %(where)s') % {
            'title': self.service.title, 'where': self.where
        }
        
