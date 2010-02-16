import threading
# from Cookie import SimpleCookie

# from data_structures import *
# from utilities import *


class Rs(threading.local):
    # b = bind
    def b(self, s, app):
        self.s = s
        self.app = app
        self.status = 200
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
