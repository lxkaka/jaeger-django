#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import opentracing.tracer
from django.conf import settings
from jaeger_client import Config

from huipy.tracer import conf


def initialize_global_tracer():
    _config = Config(
        config=conf.CONFIG,
        service_name=settings.SERVICE_NAME,
        validate=True,
    )
    if _config.initialized():
        tracer = opentracing.tracer
    else:
        tracer = _config.initialize_tracer()
    return tracer
