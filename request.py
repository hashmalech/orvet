import threading
# import cgi
from UserDict import DictMixin
# from Cookie import SimpleCookie
# from urllib import quote as urlquote
# from urlparse import urlunsplit

# from data_structures import *
# from utilities import *

# try: from cgi import parse_qs # Python 2.5
# except ImportError: from urlparse import parse_qs # Python 2.6

# from StringIO import StringIO as BytesIO
# TextIOWrapper = None

# SECURECOOKIE_KEY = "Exi1GApX"
# MEMFILE_MAX = 1024*100


class Rq(threading.local, DictMixin):
    def __init__(self):self.b({},None)
    def __getitem__(self,k):return self.environ[k]
    def __setitem__(self,k,v):self.environ[k]=v

    def b(self, e, app=None):
        self.app = app
        self.environ = e
        self.e = e
        # self._GET = self._POST = self._GETPOST = None
        # self._COOKIES = self._body = self._header = None
        # These attributes are used anyway, so it is ok to compute them here
        self.path = e.get('PATH_INFO', '/')
        if not self.path.startswith('/'):
            self.path = '/' + self.path
        self.method = e.get('REQUEST_METHOD', 'GET')

    def keys(self): return self.environ.keys()

    # @property
    # def query_string(self):
    #     return self.environ.get('QUERY_STRING', '')

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

    # @property
    # def GET(self):
    #     """ Dictionary with parsed query_string data. """
    #     if self._GET is None:
    #         data = parse_qs(self.query_string, keep_blank_values=True)
    #         self._GET = dict()
    #         for key, values in data.iteritems():
    #             for value in values:
    #                 self._GET[key] = value
    #     return self._GET

    # @property
    # def POST(self):
    #     """ Dictionary with parsed form data. """
    #     if self._POST is None:
    #         safe_env = dict() # Build a safe environment for cgi
    #         for key in ('REQUEST_METHOD', 'CONTENT_TYPE', 'CONTENT_LENGTH'):
    #             if key in self.environ:
    #                 safe_env[key] = self.environ[key]
    #         safe_env['QUERY_STRING'] = '' # Without this, sys.argv is called!
    #         if TextIOWrapper:
    #             fb = TextIOWrapper(self.body, encoding='ISO-8859-1')
    #         else:
    #             fb = self.body
    #         data = cgi.FieldStorage(fp=fb, environ=safe_env)
    #         self._POST = dict()
    #         for item in data.list:
    #             self._POST[item.name] = item if item.filename else item.value
    #     return self._POST

    # @property
    # def params(self):
    #     """ A mix of GET and POST data. POST overwrites GET """
    #     if self._GETPOST is None:
    #         self._GETPOST = dict(self.GET)
    #         self._GETPOST.update(dict(self.POST))
    #     return self._GETPOST

    # @property
    # def body(self):
    #     """ The HTTP request body as a seekable file object """
    #     if self._body is None:
    #         cl = 0 if not self['CONTENT_LENGTH'] else self['CONTENT_LENGTH']
    #         maxread = max(0, int(cl))
    #         stream = self.environ['wsgi.input']
    #         self._body = BytesIO() if maxread < MEMFILE_MAX\
    #                                else TemporaryFile(mode='w+b')
    #         while maxread > 0:
    #             part = stream.read(min(maxread, MEMFILE_MAX))
    #             if not part: #TODO: Wrong content_length. Error? Do nothing?
    #                 break
    #             self._body.write(part)
    #             maxread -= len(part)
    #         self.environ['wsgi.input'] = self._body
    #     self._body.seek(0)
    #     return self._body

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
