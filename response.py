import threading
from Cookie import SimpleCookie

# from data_structures import *
# from utilities import *


class Response(threading.local):
    def bind(self, app):
        self.app = app
        self.status = 200
        self.error = None
        self.header = dict()
        self.content_type = 'text/html; charset=UTF-8'
        self.charset = 'UTF-8'
        self.cookies = SimpleCookie()

    def headers(self):
        """Returns a WSGI conform list of header/value pairs."""
        # for c in self.cookies.values():
        #     if c.OutputString() not in self.header.getall('Set-Cookie'):
        #         self.header.append('Set-Cookie', c.OutputString())
        return list(self.header.iteritems())

    def get_content_type(self): return self.header['Content-Type']

    def set_content_type(self, value):
        if 'charset=' in value:
            self.charset = value.split('charset=')[-1].split(';')[0].strip()
        self.header['Content-Type'] = value

    content_type = property(get_content_type, set_content_type, None,
                            get_content_type.__doc__)

    def set_cookie(self, key, value, **kargs):
        if not isinstance(value, basestring):
            # sec = self.app.config['securecookie.key']
            sec = SECURECOOKIE_KEY
            value = cookie_encode(value, sec)
        self.cookies[key] = value
        for k, v in kargs.iteritems():
            self.cookies[key][k.replace('_', '-')] = v
