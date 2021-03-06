from mock import patch, MagicMock

from django.test import RequestFactory

from kuma.core.tests import KumaTestCase, eq_
from kuma.core.middleware import (
    WhiteNoiseMiddleware,
    SetRemoteAddrFromForwardedFor,
    ForceAnonymousSessionMiddleware,
    RestrictedEndpointsMiddleware,
    RestrictedWhiteNoiseMiddleware,
)


class TrailingSlashMiddlewareTestCase(KumaTestCase):
    def test_no_trailing_slash(self):
        response = self.client.get(u'/en-US/ohnoez')
        eq_(response.status_code, 404)

    def test_404_trailing_slash(self):
        response = self.client.get(u'/en-US/ohnoez/')
        eq_(response.status_code, 404)

    def test_remove_trailing_slash(self):
        response = self.client.get(u'/en-US/docs/files/?xxx=\xc3')
        eq_(response.status_code, 301)
        assert response['Location'].endswith('/en-US/docs/files?xxx=%C3%83')


class SetRemoteAddrFromForwardedForTestCase(KumaTestCase):

    def test_rate_x_forwarded_for(self):
        rf = RequestFactory()
        middleware = SetRemoteAddrFromForwardedFor()

        req1 = rf.get('/', HTTP_X_FORWARDED_FOR='1.1.1.1')
        middleware.process_request(req1)
        eq_(req1.META['REMOTE_ADDR'], '1.1.1.1')

        req2 = rf.get('/', HTTP_X_FORWARDED_FOR='2.2.2.2')
        middleware.process_request(req2)
        eq_(req2.META['REMOTE_ADDR'], '2.2.2.2')

        req3 = rf.get('/', HTTP_X_FORWARDED_FOR='3.3.3.3, 4.4.4.4')
        middleware.process_request(req3)
        eq_(req3.META['REMOTE_ADDR'], '3.3.3.3')


def test_force_anonymous_session_middleware(rf, settings):
    request = rf.get('/foo')
    request.COOKIES[settings.SESSION_COOKIE_NAME] = 'totallyfake'

    middleware = ForceAnonymousSessionMiddleware()
    middleware.process_request(request)

    assert request.session
    assert request.session.session_key is None

    response = middleware.process_response(request, MagicMock())

    assert not response.method_calls


def test_restricted_endpoints_middleware(rf, settings):
    settings.ATTACHMENT_HOST = 'demos'
    settings.ENABLE_RESTRICTIONS_BY_HOST = True
    middleware = RestrictedEndpointsMiddleware()

    request = rf.get('/foo', HTTP_HOST='demos')
    middleware.process_request(request)
    assert request.urlconf == 'kuma.urls_untrusted'

    request = rf.get('/foo', HTTP_HOST='not-demos')
    middleware.process_request(request)
    assert not hasattr(request, 'urlconf')

    settings.ENABLE_RESTRICTIONS_BY_HOST = False
    request = rf.get('/foo', HTTP_HOST='demos')
    middleware.process_request(request)
    assert not hasattr(request, 'urlconf')


def test_restricted_whitenoise_middleware(rf, settings):
    settings.ATTACHMENT_HOST = 'demos'
    settings.ENABLE_RESTRICTIONS_BY_HOST = True
    middleware = RestrictedWhiteNoiseMiddleware()

    sentinel = object()

    with patch.object(WhiteNoiseMiddleware, 'process_request',
                      return_value=sentinel):
        request = rf.get('/foo', HTTP_HOST='demos')
        assert middleware.process_request(request) is None

        request = rf.get('/foo', HTTP_HOST='not-demos')
        assert middleware.process_request(request) is sentinel

        settings.ENABLE_RESTRICTIONS_BY_HOST = False
        request = rf.get('/foo', HTTP_HOST='demos')
        assert middleware.process_request(request) is sentinel
