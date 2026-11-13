"""Reverse proxy support: honor X-Forwarded-For and X-Forwarded-Proto only from the addresses in FORWARDED_ALLOW_IPS."""
import ipaddress

from werkzeug.middleware.proxy_fix import ProxyFix


class TrustedProxyFix:
    """Werkzeug's ProxyFix, applied only to requests whose REMOTE_ADDR is a trusted proxy, so no other client can
    set its own IP or scheme with forwarded headers. ProxyFix rewrites REMOTE_ADDR in the request's environ, which
    Gunicorn's access log reads after the response."""

    def __init__(self, app, networks):
        """networks comes from config.trusted_networks(): a list of networks, or None to trust every address."""
        self.app = app
        self.proxied = ProxyFix(app, x_for=1, x_proto=1)
        self.networks = networks

    def is_trusted(self, address):
        if self.networks is None:
            return True
        try:
            ip = ipaddress.ip_address(address)
        except ValueError:
            return False
        # An IPv4 client on a dual-stack socket arrives as ::ffff:a.b.c.d
        ip = getattr(ip, 'ipv4_mapped', None) or ip
        return any(ip in network for network in self.networks)

    def __call__(self, environ, start_response):
        app = self.proxied if self.is_trusted(environ.get('REMOTE_ADDR', '')) else self.app
        return app(environ, start_response)
