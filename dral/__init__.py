# pkgutil-style namespace package: this "dral" top-level package is shared
# with the separate dral-model runtime distribution (dral/model). Keep this
# file identical across both distributions - see d-ral-model-python/dral/__init__.py.
__path__ = __import__("pkgutil").extend_path(__path__, __name__)
