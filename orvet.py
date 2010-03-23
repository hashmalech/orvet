import cgi
from cgi import parse_qs as qs
import threading
import inspect
import base64
import hmac
import cPickle as pickle
from Cookie import SimpleCookie
from traceback import format_exc as t
from UserDict import DictMixin
# from urllib import quote as urlquote
# from urlparse import urlunsplit
from StringIO import StringIO as BytesIO


TextIOWrapper = None
MEMFILE_MAX = 1024*100


from router import Rt


def status(s):
    status_dict={200:'OK',404:'NOT FOUND',500:'INTERNAL SERVER ERROR'}
    return "%s %s" % (s, status_dict[s])


def cookie_encode(d, k):m=base64.b64encode(pickle.dumps(d,-1));\
    s=base64.b64encode(hmac.new(k,m).digest());return'!%s?%s'%(s,m)


def cookie_decode(data, k):
    s, m = data.split('?',1)
    v=s[1:]==base64.b64encode(hmac.new(k,m).digest())
    if v:return pickle.loads(base64.b64decode(m))


def start_err():rq.e['wsgi.errors']=t();\
    rs.s(status(500),[('Content-Type','text/plain')]);return t()


class Rq(threading.local, DictMixin):
    def __init__(self):self.b({},None)

    def __getitem__(self,k):
        if not self.sk.has_key(k):return self.e[k]
        elif inspect.ismethod(self.sk[k]):self.sk[k]=self.sk[k]()
        return self.sk[k]

    def __setitem__(self,k,v):raise

    def b(self, e, app=None):
        self.app=app;self.e=e
        self.sk={'QUERY_STRING':self.query_string,'GET':self.kGET,
                 'POST':self.kPOST,'PARAMS':self.kparams,'BODY':self.kbody,
                 'COOKIES':self.kcookies}
        # self._COOKIES = self._header = None
        self.path=e.get('PATH_INFO', '/')
        if not self.path.startswith('/'):self.path='/'+self.path
        self.method = e.get('REQUEST_METHOD', 'GET')

    def query_string(self):return self.e.get('QUERY_STRING', '')

    def kPOST(self):
        safe_env = {} # Build a safe environment for cgi
        for key in ('REQUEST_METHOD', 'CONTENT_TYPE', 'CONTENT_LENGTH'):
            if key in self.e:
                safe_env[key] = self.e[key]
        safe_env['QUERY_STRING'] = '' # Without this, sys.argv is called!
        if TextIOWrapper:
            fb = TextIOWrapper(self.body, encoding='ISO-8859-1')
        else:
            fb = self.body
        data = cgi.FieldStorage(fp=fb, environ=safe_env)
        POST = dict()
        for item in data.list:
            POST[item.name] = item if item.filename else item.value
        return POST

    def kGET(self):return qs(self['QUERY_STRING'],keep_blank_values=True)

    @property
    def params(self):return self['PARAMS']
    def kparams(self):p=self['GET'];p.update(self['POST']);return p

    # @property
    # def fullpath(self):
    #     """ Request path including SCRIPT_NAME (if present) """
    #     return self.environ.get('SCRIPT_NAME', '').rstrip('/') + self.path

    # @property
    # def url(self):
    #     """ The full URL as requested by the client """
    #     scheme = self.environ.get('wsgi.url_scheme', 'http')
    #     host   = self.environ.get('HTTP_HOST', None)
    #     if not host:
    #         host = self.environ.get('SERVER_NAME')
    #         port = self.environ.get('SERVER_PORT', '80')
    #         if scheme + port not in ('https443', 'http80'):
    #             host += ':' + port
    #     parts = (scheme, host, urlquote(self.fullpath), self.query_string, '')
    #     return urlunsplit(parts)

    # @property
    # def body_length(self):
    #     """ The Content-Length header as an integer, -1 if not specified """
    #     return int(self.environ.get('CONTENT_LENGTH', -1))

    # @property
    # def header(self):
    #     ''' Dictionary containing HTTP headers'''
    #     if self._header is None:
    #         self._header = MultiDict()
    #         for key, value in self.environ.iteritems():
    #             if key.startswith('HTTP_'):
    #                 key = key[5:].replace('_','-').title()
    #                 self._header[key] = value
    #     return self._header

    @property
    def body(self):return self['BODY']
    def kbody(self):
        cl = 0 if not self['CONTENT_LENGTH'] else self['CONTENT_LENGTH']
        maxread = max(0, int(cl))
        stream = self.e['wsgi.input']
        body = BytesIO() if maxread < MEMFILE_MAX\
                         else TemporaryFile(mode='w+b')
        while maxread > 0:
            part = stream.read(min(maxread, MEMFILE_MAX))
            if not part: #TODO: Wrong content_length. Error? Do nothing?
                break
            body.write(part)
            maxread -= len(part)
        self.e['wsgi.input'] = body

        body.seek(0)
        return body

    def kcookies(self):
        d=SimpleCookie(self.e.get('HTTP_COOKIE',''));c={}
        for i in d.itervalues():c[i.key]=i.value
        return c

    def get_cookie(self, *a):
        v=self['COOKIES'].get(*a)
        s=self.app.config['SECURECOOKIE_KEY']
        d=cookie_decode(v,s)
        return d


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
        p = p.lstrip('/')
        p = p.split('?')[0]
        self.routes.setdefault(method,Rt()).add(p, h, **k)

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
