import traceback

from router import Router
from request import Request
from response import Response


class Orvet:
    def __init__(self):
        self.routes = {}
        # self.default_route = None
        # self.error_handler = {}
        # self.config = dict()

    # e = environ
    # s = start_response
    # r = response
    # b = body
    def __call__(self, e, s):
        r, b = self.h(e)
        s(status(r.status), r.headers())
        return self.i(b)

    def add_route(self, handler, path, method='GET', **k):
        path = path.lstrip('/')
        self.routes.setdefault(method, Router()).add(path, handler, **k)

    def handle(self):
        handler, args = self.match_url(request.path, request.method)
        if not handler:
            return HTTPError(status(404))
        if not args:
            args = dict()
        return handler(**args)

    # e = environ
    # b = body
    def h(self, e):
        request.bind(e, self)
        response.bind(self)
        b = self.handle(request.path, request.method)
        if not b and response.status == 200:
            response.status = 404
        return response, b

    def i(self, d):
        return [d]

    # p = path
    # m = method
    # t = tests
    # ha = handler
    # pa = params
    def match_url(self, p, method='GET'):
        p = p.lstrip('/')
        m = method
        t = (m,'GET','ALL') if m == 'HEAD' else (m,'ALL')
        for m in t:
            if m in self.routes:
                ha, pa = self.routes[m].match(p)
                if ha:
                    return ha, pa
        return None, None


app = Orvet()


request = Request()
response = Response()


def status(s):
    return str(s)
