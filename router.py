import re


class BottleException(Exception):
    """ A base class for exceptions used by bottle. """
    pass


class RouteError(BottleException):
    """ This is a base class for all routing related exceptions """


class RouteSyntaxError(RouteError):
    """ The route parser found something not supported by this router """


class RouteBuildError(RouteError):
    """ The route could not been build """


class Rt(object):
    ''' A route associates a string (e.g. URL) with an object (e.g. function)
    Dynamic routes use regular expressions to describe all matching strings.
    Some dynamic routes may extract parts of the string and provide them as
    data. This router matches a string against multiple routes and returns
    the associated object along with the extracted data. 
    '''

    syntax = re.compile(r'(?P<pre>.*?)'
                        r'(?P<escape>\\)?'
                        r':(?P<name>[a-zA-Z_]+)?'
                        r'(#(?P<rex>.*?)#)?')

    def __init__(self):
        self.static = dict()
        self.dynamic = []
        self.splits = dict()

    def is_dynamic(self, route):
        ''' Returns True if the route contains dynamic syntax '''
        for text, name, rex in self.itersplit(route):
            if name or rex:
                return True
        return False

    def split(self, route):
        ''' Splits a route into (prefix, parameter name, pattern) triples.
            The prefix may be empty. The other two may be None. '''
        return list(self.itersplit(route))

    def itersplit(self, route):
        ''' Same as Router.split() but returns an iterator. '''
        match = None
        for match in self.syntax.finditer(route):
            pre = match.group('pre')
            name = match.group('name')
            rex = match.group('rex')
            if match.group('escape'):
                yield match.group(0).replace('\\:',':',1), None, None
                continue
            if rex:
                rex = re.sub(r'\(\?P<[^>]*>', '(?:', rex)
                rex = re.sub(r'\((?!\?)', '(?:', rex)
                try:
                    rex = re.compile(rex)
                except re.error, e:
                    raise RouteSyntaxError(
                          "Syntax error in '%s' offset %d: %s"
                          % (route, match.start('rex'), repr(e)))
                if rex.groups > 1: # Should not be possible.
                    raise RouteSyntaxError("Groups in route '%s'." % (route))
            yield pre, name, rex
        if not match:
            yield route, None, None
        elif match.end() < len(route):
            yield route[match.end():], None, None

    def parse(self, route):
        ''' Parses a route and returns a tuple. The first element is a
        RegexObject with named groups. The second is a non-grouping version
        of that RegexObject.'''
        rexp = ''
        fexp = ''
        isdyn = False
        for text, name, rex in self.itersplit(route):
            rexp += re.escape(text)
            fexp += re.escape(text)
            if name and rex:
                rexp += '(?P<%s>%s)' % (name, rex.pattern)
                fexp += '(?:%s)' % rex.pattern
            elif name:
                rexp += '(?P<%s>[^/]+)' % name
                fexp += '[^/]+'
            elif rex:
                rexp += '(?:%s)' % rex.pattern
                fexp += '(?:%s)' % rex.pattern
        return re.compile('%s' % rexp), re.compile('%s' % fexp)

    def add(self, route, data, static=False, name=None):
        ''' Adds a route to the router. Syntax:
                `:name` matches everything up to the next slash.
                `:name#regexp#` matches a regular expression.
                `:#regexp#` creates an anonymous match.
                A backslash can be used to escape the `:` character.
        '''
        if not self.is_dynamic(route) or static:
            self.static[route] = data
            return
        rexp, fexp = self.parse(route)
        rexp = re.compile('^(%s)$' % rexp.pattern)
        if not rexp.groupindex:
            rexp = None # No named groups -> Nothing to extract
        if fexp.groups: # Should not be possible.
            raise RouteSyntaxError("Route contains groups '%s'." % (route))
        try:
            big_re, subroutes = self.dynamic[-1]
            big_re = '%s|(^%s$)' % (big_re.pattern, fexp.pattern)
            big_re = re.compile(big_re)
            subroutes.append((data, rexp))
            self.dynamic[-1] = (big_re, subroutes)
        except (AssertionError, IndexError), e:
            # AssertionError: To many groups
            self.dynamic.append((re.compile('(^%s$)' % fexp.pattern),
                                 [(data, rexp)]))
        if name:
            self.splits[name] = self.split(route)

    def match(self, uri):
        ''' Matches an URL and returns a (handler, data) tuple '''
        if uri in self.static:
            return self.static[uri], {}
        for big_re, subroutes in self.dynamic:
            match = big_re.match(uri)
            if match:
                data, group_re = subroutes[match.lastindex - 1]
                if not group_re:
                    return data, {}
                group_match = group_re.match(uri)
                if not group_match:
                    return None, {}
                return data, group_match.groupdict()
        return None, {}

    def build(self, route_name, **args):
        ''' Builds an URL out of a named route and some parameters.'''
        if route_name not in self.splits:
           raise RouteBuildError(
                 "No route found with name '%s'." % route_name)
        out = []
        for text, key, rex in self.splits[route_name]:
            out.append(text)
            if key and key not in args:
                raise RouteBuildError("Missing parameter '%s' in route '%s'"
                    % (key, route_name))
            if rex and not key:
                raise RouteBuildError("Anonymous pattern found. Can't "
                    "generate the route '%s'." % route_name)
            #TODO: Do this in add()
            if rex and not re.match('^%s$' % rex.pattern, args[key]):
                raise RouteBuildError("Parameter '%s' does not match pattern "
                    "for route '%s': '%s'" % (key, route_name, rex.pattern))
            if key:
                out.append(args[key])
        return ''.join(out)
