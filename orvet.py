from traceback import format_exc as ET

from router import Rt
from request import Rq
from response import Rs


class StatusError(Exception):
    def __init__(self,s=500):start_err(s)


def start_err(s):rq.e['wsgi.errors'].write(ET());rs.s(status(s),[])


class Orvet:
    def __init__(self):
        self.routes = {}
        # self.default_route = None
        # self.error_handler = {}
        # self.config = dict()

    # e = environ, s = start_response, r = response, b = body, t = traceback
    def __call__(self,e,s):
        try:r,b=self.h(e,s);s(status(r.status),r.headers());return self.i(b)
        except StatusError:return[ET()]
        except Exception:start_err(500);return[ET()]

    # p = path, h = handler
    def add_route(self, p, h, method='GET', **k):
        self.routes.setdefault(method, Rt()).add(p.lstrip('/'), h, **k)

    # p = path, m = method, h = handler, a = args
    def handle(self,p,m):
        h,a=self.mu(p,m)
        if h:return h(**a)
        else:rs.status=404

    # e = environ, b = body
    def h(self, e, s):
        request.b(e,self);response.b(s, self)
        b = self.handle(request.path, request.method)
        if not b and response.status == 200:
            response.status = 404
        return response, b

    # This method should convert the response body to an iterable
    # d = data
    def i(self,d):d=d or'';return[d]

    # p = path, m = method, t = tests, h = handler, a = params
    def mu(self, p, method='GET'):
        p,m=p.lstrip('/'),method
        t=(m,'GET','ALL')if m=='HEAD'else(m,'ALL')
        for m in t:
            if m in self.routes:
                h,a=self.routes[m].match(p)
                if not a:a={}
                if h:return h,a
        return None,None


app = Orvet()


request = rq = Rq()
response = rs = Rs()


def status(s):
    return str(s)
