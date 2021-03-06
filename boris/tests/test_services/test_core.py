'''
Created on 22.10.2011

@author: xaralis
'''
from django.test import TestCase
from nose import tools

from boris.services.models.core import Service, service_list, get_model_for_class_name
from boris.clients.models import Client, Anonymous
from models import DummyServiceClass, ModelDummy, DummyLimitedServiceClass, Dummy1, Dummy2


class TestServiceMetaClass(TestCase):
    def setUp(self):
        pass

    def test_clientservice_subclass_is_registered_after_declaration(self):
        tools.assert_true(DummyServiceClass in Service.registered_services)

    def test_common_model_subclass_is_not_registered_after_declaration(self):
        tools.assert_false(ModelDummy in Service.registered_services)

    def test_subclassing_clientservice_adds_service_meta_class(self):
        tools.assert_true(hasattr(DummyServiceClass, 'service'))
        service_meta = DummyServiceClass.service

        tools.assert_true(hasattr(service_meta, 'title'))
        tools.assert_true(hasattr(service_meta, 'description_template'))
        tools.assert_true(hasattr(service_meta, 'is_available'))


class TestServiceOptions(TestCase):
    def setUp(self):
        self.subcls = DummyServiceClass
        self.subcls_limited = DummyLimitedServiceClass

    def test_description_template_fallback(self):
        tools.assert_true(
            'services/desc/aaa.html' in self.subcls.service.get_description_template_list()
        )
        tools.assert_true(len(self.subcls.service.get_description_template_list()) > 1)

    def test_is_available_uses_defined_callback(self):
        tools.assert_true(self.subcls.service.is_available(1))
        tools.assert_false(self.subcls.service.is_available(2))

    def test_limited_to_passes(self):
        tools.assert_true(self.subcls_limited.service.is_available(Client()))

    def test_limited_to_blocks(self):
        tools.assert_false(self.subcls_limited.service.is_available(Anonymous()))

    def test_is_available_works_with_limited_to(self):
        c = Client()
        c.failme = True
        tools.assert_false(self.subcls_limited.service.is_available(c))


class TestUtilityMethods(TestCase):
    def setUp(self):
        self.d1 = Dummy1
        self.d2 = Dummy2

    def test_service_list(self):
        avail_s_list = service_list(Client())
        tools.assert_true(self.d2 in avail_s_list)
        tools.assert_false(self.d1 in avail_s_list)

        all_s_list = service_list()
        tools.assert_true(self.d2 in all_s_list)
        tools.assert_true(self.d1 in all_s_list)

    def test_get_model_for_class_name_returns_correct_class(self):
        tools.assert_equals(get_model_for_class_name('Dummy1'), self.d1)
        tools.assert_equals(get_model_for_class_name('Dummy2'), self.d2)

    @tools.raises(ValueError)
    def test_get_model_for_class_name_raises_valueerror_for_non_registered_class(self):
        get_model_for_class_name('Dummy3')

