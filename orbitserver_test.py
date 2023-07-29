#!/usr/bin/env python3

import tornado.testing
import orbitserver

class TestMainHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        app = orbitserver.make_app()
        app.logger = tornado.log.app_log
        return app

    def get_url(self, path):
        """Returns an absolute url for the given path on the test server."""
        return '%s://localhost:%s%s' % (self.get_protocol(),
                                        self.get_http_port(), path)

    def test_mainhandler_noparams(self):
        httpresponse = self.fetch("/")
        assert httpresponse.code == 422

    def test_mainhandler_mm(self):
        httpresponse = self.fetch("/?mm=12&e=0&i=45&raan=0&aop=0&ma=0")
        assert httpresponse.code == 200

    def test_mainhandler_a(self):
        httpresponse = self.fetch("/?a=6483824&e=0&i=45&raan=0&aop=0&ta=0")
        assert httpresponse.code == 200
