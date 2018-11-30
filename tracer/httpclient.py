#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging

import opentracing
import requests
import time

from django.conf import settings
from opentracing import Format
from opentracing.ext import tags
from requests import HTTPError
from requests.adapters import HTTPAdapter
from urllib3.util import parse_url


from huipy.logger import request_logger
from huipy.tracer.initial_tracer import initialize_global_tracer
from huipy.tracer.request_context import get_current_span

logger = logging.getLogger(__name__)


def before_http_request(request):
    """
    :param request:
    :type request: Request.request
    :return: returns child tracing span encapsulating this request
    """
    tracer = initialize_global_tracer()
    parent_span = get_current_span()
    scheme, auth, host, port, path, query, fragment = parse_url(request.url)
    operation_name = '{} {}'.format(request.method, path)
    span = tracer.start_span(
        operation_name=operation_name,
        child_of=parent_span
    )
    span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)
    span.set_tag(tags.HTTP_URL, request.url)
    span.set_tag(tags.HTTP_METHOD, request.method)
    if host:
        span.set_tag(tags.PEER_HOST_IPV4, host)
    if port:
        span.set_tag(tags.PEER_PORT, port)

    carrier = {}
    try:
        tracer.inject(
            span_context=span.context,
            format=Format.HTTP_HEADERS,
            carrier=carrier
        )
        for key, value in carrier.items():
            request.headers.update({key: value})
    except opentracing.UnsupportedFormatException:
        pass
    return span


class HttpClient(object):
    _headers = {
        'Content-Type': 'application/json',
    }
    _start = None

    def __init__(self, url, data=None, headers=_headers, retry=0, timeout=10):
        self.url = url
        self.data = data
        self.headers = headers
        self.retry = retry
        self.timeout = timeout

    def handle_request(self, method='GET', params=None, data=None, **kwargs):
        req = requests.Request(method=method, url=self.url, headers=self.headers, params=params, data=data, **kwargs)
        request = req.prepare()
        span = before_http_request(request)
        session = requests.session()
        adapter = HTTPAdapter(max_retries=self.retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        response = session.send(request, timeout=self.timeout)
        if response and span:
            span.set_tag(tags.HTTP_STATUS_CODE, response.status_code)
            span.finish()
        return response

    def get(self, **kwargs):
        self._start = time.time()
        response = self.handle_request(method='GET', params=self.data, **kwargs)
        return self._check_response(response)

    def post(self, **kwargs):
        self._start = time.time()
        response = self.handle_request(method='POST', data=self.data, **kwargs)
        return self._check_response(response)

    def patch(self, **kwargs):
        self._start = time.time()
        response = self.handle_request(method='PATCH', data=self.data, **kwargs)
        return self._check_response(response)

    def delete(self, **kwargs):
        self._start = time.time()
        response = self.handle_request(method='DELETE', params=self.data, **kwargs)
        return self._check_response(response)

    def _check_response(self, response):
        try:

            duration = int((time.time() - self._start) * 1000)
            body = json.dumps(response.request.body.decode()) if isinstance(response.request.body, bytes) else '-'
            request_logger.info(
                '{method} {duration} {url} ${body}$ {status_code} "{reason}" ${res_content}$ {service_name}'.format(
                    method=response.request.method,
                    duration=duration,
                    url=response.request.url,
                    body=body,
                    status_code=response.status_code,
                    reason=response.reason,
                    res_content=response.json(),
                    service_name=settings.SERVICE_NAME
                ),
            )
        except Exception as e:
            logger.error(e)
        if response.status_code != 200:
            raise ServiceError(response.text, response=response)
        return response


class ServiceError(HTTPError):
    """requests错误"""
