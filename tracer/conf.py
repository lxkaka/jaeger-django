#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.conf import settings

if not settings.configured:
    settings.configure()

SAMPLE_TYPE = 'const'
if hasattr(settings, 'SAMPLE_TYPE'):
    sample_type = settings.SAMPLE_TYPE

SAMPLE_PARAM = 1
if hasattr(settings, 'SAMPLE_PARAM'):
    SAMPLE_PARAM = settings.SAMPLE_PARAM

TRACE_ID_HEADER = 'zaihui-trace-id'
if hasattr(settings, 'TRACE_ID_HEADER'):
    TRACE_ID_HEADER = settings.TRACE_ID_HEADER

BAGGAGE_HEADER_PREFIX = 'zaihui-'
if hasattr(settings, 'BAGGAGE_HEADER_PREFIX'):
    BAGGAGE_HEADER_PREFIX = settings.BAGGAGE_HEADER_PREFIX

if not hasattr(settings, 'SERVICE_NAME'):
    settings.SERVICE_NAME = 'TEST'

REPORTING_HOST = 'localhost'
if hasattr(settings, 'JAEGER_REPORTING_HOST'):
    REPORTING_HOST = settings.JAEGER_REPORTING_HOST

CONFIG = {
    'sampler': {
        'type': SAMPLE_TYPE,
        'param': SAMPLE_PARAM,
    },
    'local_agent': {
        'reporting_host': REPORTING_HOST,
    },
    'trace_id_header': TRACE_ID_HEADER,
    'baggage_header_prefix': BAGGAGE_HEADER_PREFIX,
}
