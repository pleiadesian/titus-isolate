import os

from titus_isolate.config.property_provider import PropertyProvider


class EnvPropertyProvider(PropertyProvider):

    @staticmethod
    def get(key):
        return os.environ.get(key, None)
