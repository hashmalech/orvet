import threading
import base64
import hmac
import cPickle as pickle
from Cookie import SimpleCookie
from traceback import format_exc as t

from router import Rt
from request import Rq


def status(s):
    status_dict = {
        200: 'OK',
        404: 'NOT FOUND',
        500: 'INTERNAL SERVER ERROR'
    }
    return "%s %s" % (s, status_dict[s])


def cookie_encode(d, k):
    m=base64.b64encode(pickle.dumps(d,-1))
    s=base64.b64encode(hmac.new(k,m).digest())
    return'!%s?%s'%(s,m)


def cookie_decode(data, k):
    s, m = data.split('?',1)
    v=s[1:]==base64.b64encode(hmac.new(k,m).digest())
    if v:return pickle.loads(base64.b64decode(m))


def start_err(): rq.e['wsgi.errors']=t();rs.s(status(500),[]);return t()


class Rs(threading.local):
    def b(self, s, app):
        self.s=s;self.app=app;self.status=status(200);self.header={}
        self.content_type='text/html; charset=UTF-8'
        self.cookies=SimpleCookie()

    def headers(self):
        a=map(lambda c:('Set-Cookie',c.OutputString()),self.cookies.values())
        return list(self.header.iteritems())+a

    def c(self):return self.header['Content-Type']
    def d(self, v):self.header['Content-Type']=v
    content_type=property(c,d,None,c.__doc__)

    def set_cookie(self, k, v, **kargs):
        self.cookies[k]=cookie_encode(v,self.app.config['SECURECOOKIE_KEY'])
        for i,j in kargs.iteritems():self.cookies[k][i.replace('_','-')]=j


class Orvet:
    def __init__(self):self.routes={};self.config={'SECURECOOKIE_KEY':'None'}

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
        response.set_cookie('ORLY', 'YARLY')
        return "Hello, world!"
    app.add_route('/', index)

    validator_app = validator(app)

    httpd = make_server('', 8080, validator_app)
    print "Listening on port 8080..."
    httpd.serve_forever()
