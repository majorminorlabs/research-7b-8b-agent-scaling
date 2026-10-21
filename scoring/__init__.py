"""Allow the current scorer and frozen reference scorer to share this namespace."""
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)
