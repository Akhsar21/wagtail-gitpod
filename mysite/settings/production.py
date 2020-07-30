from __future__ import absolute_import, unicode_literals
from .base import *
import dj_database_url
import os

env = os.environ.copy()
SECRET_KEY = env['SECRET_KEY']

DEBUG = False

# Allow all host headers
ALLOWED_HOSTS = ['aksar-as.herokuapp.com', '127.0.0.1']

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

COMPRESS_OFFLINE = True
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
]

#DTABASES = {
#    'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
#}

COMPRESS_CSS_HASHING_METHOD = 'content'

SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_REFERRER_POLICY =

try:
    from .local import *
except ImportError:
    pass
