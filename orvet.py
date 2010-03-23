import threading
# from Cookie import SimpleCookie

# from data_structures import *
# from utilities import *

from traceback import format_exc as t

from router import Rt
from request import Rq
# from response import Rs


def status(s):
    status_dict = {
        200: 'OK',
        404: 'NOT FOUND',
        500: 'INTERNAL SERVER ERROR'
    }
    return "%s %s" % (s, status_dict[s])


def start_err(): rq.e['wsgi.errors']=t();rs.s(status(500),[]);return t()


class Rs(threading.local):
    # b = bind
    def b(self, s, app):
        self.s = s
        self.app = app
        self.status = status(200)
        # self.error = None
        self.header = dict()
        self.content_type = 'text/html; charset=UTF-8'
        self.charset = 'UTF-8'
        # self.cookies = SimpleCookie()

    def headers(self):
        # for c in self.cookies.values():
        #     if c.OutputString() not in self.header.getall('Set-Cookie'):
        #         self.header.append('Set-Cookie', c.OutputString())
        return list(self.header.iteritems())

    # get_content_type
    def c(self): return self.header['Content-Type']

    # set_content_type
    def d(self, v):
        if 'charset=' in v:
            self.charset = v.split('charset=')[-1].split(';')[0].strip()
        self.header['Content-Type'] = v

    content_type = property(c, d, None, c.__doc__)

    # def set_cookie(self, key, value, **kargs):
    #     if not isinstance(value, basestring):
    #         # sec = self.app.config['securecookie.key']
    #         sec = SECURECOOKIE_KEY
    #         value = cookie_encode(value, sec)
    #     self.cookies[key] = value
    #     for k, v in kargs.iteritems():
    #         self.cookies[key][k.replace('_', '-')] = v


class Orvet:
    def __init__(self):self.routes={};self.config={}

    def __call__(self,e,s):
        try:r,b=self.h(e,s);s(r.status,r.headers());return self.i(b)
        except Exception:return[start_err()]

    def add_route(self, p, h, method='GET', **k):
        self.routes.setdefault(method,Rt()).add(p.lstrip('/'), h, **k)

    def h(self, e, s):
        rq.b(e,self);rs.b(s,self);h,a=self.m(rq.path,rq.method)
        if h:b=h(**a)
        else:rs.status=status(404);b=None
        return rs,b

    def i(self,d):d=d or'';return[d]

    def m(self, p, m):
        p=p.lstrip('/');h=None
        if m in self.routes:h,a=self.routes[m].match(p)
        return(h,a)if h else(None,{})


app = Orvet()
request = rq = Rq()
response = rs = Rs()


if __name__ == '__main__':
    from wsgiref.validate import validator
    from wsgiref.simple_server import make_server

    def index():
        return "Hello, world!"
    app.add_route('/', index)

    validator_app = validator(app)

    httpd = make_server('', 8080, validator_app)
    print "Listening on port 8080..."
    httpd.serve_forever()
