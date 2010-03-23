import threading
import inspect
import cgi
from UserDict import DictMixin
# from Cookie import SimpleCookie
# from urllib import quote as urlquote
# from urlparse import urlunsplit

from cgi import parse_qs as qs

from StringIO import StringIO as BytesIO
TextIOWrapper = None

MEMFILE_MAX = 1024*100


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
                 'POST':self.kPOST,'PARAMS':self.kparams,'BODY':self.kbody}
        # self._COOKIES = self._header = None
        self.path=e.get('PATH_INFO', '/')
        if not self.path.startswith('/'):
            self.path = '/' + self.path
        self.method = e.get('REQUEST_METHOD', 'GET')

    def query_string(self):return self.e.get('QUERY_STRING', '')

    @property
    def POST(self):return self['POST']
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

    @property
    def GET(self):return self['GET']
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

    # @property
    # def auth(self): #TODO: Tests and docs. Add support for digest. namedtuple?
    #     """ HTTP authorisation data as a named tuple. (experimental) """
    #     return parse_auth(self.environ.get('HTTP_AUTHORIZATION'))

    # @property
    # def COOKIES(self):
    #     """ Dictionary with parsed cookie data. """
    #     if self._COOKIES is None:
    #         raw_dict = SimpleCookie(self.environ.get('HTTP_COOKIE',''))
    #         self._COOKIES = {}
    #         for cookie in raw_dict.itervalues():
    #             self._COOKIES[cookie.key] = cookie.value
    #     return self._COOKIES

    # def get_cookie(self, *args):
    #     value = self.COOKIES.get(*args)
    #     # sec = self.app.config['securecookie.key']
    #     sec = SECURECOOKIE_KEY
    #     dec = cookie_decode(value, sec)
    #     return dec or value
