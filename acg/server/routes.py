from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPFound,
)
from pyramid.security import (
    Allow,
    Everyone,
)


def includeme(config):
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
