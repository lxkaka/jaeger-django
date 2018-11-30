#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

import requests
from django.test.client import RequestFactory
from jaeger_client import Config

from huipy.tracer.httpclient import before_http_request
from huipy.tracer.middleware import TraceMiddleware
from huipy.tracer.request_context import get_current_span


class InboundTests(unittest.TestCase):
    def setUp(self):
        # settings.configure()
        self.factory = RequestFactory()

    def tearDown(self):
        Config._initialized = False

    def test_middleware_span(self):
        request = self.factory.get('/')
        TraceMiddleware().process_request(request)
        span = get_current_span()
        self.assertTrue(span.span_id)
        self.assertEqual(span.operation_name, 'GET /')

    def test_before_request(self):
        request = self.factory.get('/')
        TraceMiddleware().process_request(request)
        req = requests.Request(method='GET', url='http://127.0.0.1')
        request = req.prepare()
        span = before_http_request(request)
        self.assertTrue(span.parent_id)
        self.assertTrue(span.span_id)
        self.assertEqual(span.operation_name, 'GET /')
