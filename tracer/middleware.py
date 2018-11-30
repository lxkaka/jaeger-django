#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import urllib

try:
    # Django >= 1.10
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    # Not required for Django <= 1.9, see:
    # https://docs.djangoproject.com/en/1.10/topics/http/middleware/#upgrading-pre-django-1-10-style-middleware
    MiddlewareMixin = object
from opentracing import Format
from opentracing.ext import tags

from huipy.tracer.request_context import get_current_span, span_in_context, span_out_context


class TraceMiddleware(MiddlewareMixin):
    """"use jaeger_client realizing tracing"""

    def __init__(self, get_response=None):
        self.get_response = get_response
        self._tracer = None

    @staticmethod
    def _parse_wsgi_headers(request):
        """
        HTTP headers are presented in WSGI environment with 'HTTP_' prefix.
        This method finds those headers, removes the prefix, converts
        underscores to dashes, and converts to lower case.
        :param request:
        :return: returns a dictionary of headers
        """
        prefix = 'HTTP_'
        p_len = len(prefix)
        # use .items() despite suspected memory pressure bc GC occasionally
        # collects wsgi_environ.iteritems() during iteration.
        headers = {
            key[p_len:].replace('_', '-').lower():
                val for (key, val) in request.environ.items()
            if key.startswith(prefix)}
        setattr(request, 'headers', headers)

    @staticmethod
    def full_url(request):
        """
        Taken from
        http://legacy.python.org/dev/peps/pep-3333/#url-reconstruction
        :return: Reconstructed URL from WSGI environment.
        """
        environ = request.environ
        url = environ['wsgi.url_scheme'] + '://'

        if environ.get('HTTP_HOST'):
            url += environ['HTTP_HOST']
        else:
            url += environ['SERVER_NAME']

            if environ['wsgi.url_scheme'] == 'https':
                if environ['SERVER_PORT'] != '443':
                    url += ':' + environ['SERVER_PORT']
            else:
                if environ['SERVER_PORT'] != '80':
                    url += ':' + environ['SERVER_PORT']

        url += urllib.parse.quote(environ.get('SCRIPT_NAME', ''))
        url += urllib.parse.quote(environ.get('PATH_INFO', ''))
        if environ.get('QUERY_STRING'):
            url += '?' + environ['QUERY_STRING']
        setattr(request, 'full_url', url)

    def process_request(self, request):
        from huipy.tracer.initial_tracer import initialize_global_tracer
        self._tracer = initialize_global_tracer()
        self._parse_wsgi_headers(request)
        self.full_url(request)
        tags_dict = {
            tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER,
            tags.HTTP_URL: request.full_url,
            tags.HTTP_METHOD: request.method,
        }

        remote_ip = request.environ.get('REMOTE_ADDR')
        if remote_ip:
            tags_dict[tags.PEER_HOST_IPV4] = remote_ip

        remote_port = request.environ.get('REMOTE_PORT')
        if remote_port:
            tags_dict[tags.PEER_PORT] = remote_port
        try:
            parent_ctx = self._tracer.extract(
                Format.HTTP_HEADERS,
                carrier=request.headers
            )
        except Exception as e:
            logging.exception('trace extract failed:{}'.format(e))
            parent_ctx = None

        operation_name = '{} {}'.format(request.method, request.path)
        span = self._tracer.start_span(
            operation_name=operation_name,
            child_of=parent_ctx,
            tags=tags_dict)
        span_in_context(span)

    def process_response(self, request, response):
        span = get_current_span()
        if span:
            span.set_tag(tags.HTTP_STATUS_CODE, response.status_code)
            span.finish()
            span_out_context()

        else:
            logging.exception('can not get valid span')
        return response
