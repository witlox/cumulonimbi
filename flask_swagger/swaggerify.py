from collections import OrderedDict

__author__ = 'Johannes'

# noinspection PyPackageRequirements
from bson.json_util import dumps


class SwaggerInfoBorg:
    def __init__(self):
        self.api_version = '1.0.0'
        self.api_title = "Cumulonimbi Job Manager API"
        self.api_description = "The API for consumers of Cumulonimbi to use"
        self.api_tos = "http://example.com"
        self.api_contact_name = "Pim Witlox & Johannes Bertens"
        self.api_license_name = "proprietary"
        self.api_host = "localhost:5000"
        self.api_basePath = "/"
        self.api_schemes = ["http"]
        self.api_paths = None

    def generate_object(self):
        return OrderedDict([
            ('swagger', '2.0'),
            ('info', OrderedDict([
                ('version', self.api_version),
                ('title', self.api_title),
                ('description', self.api_description),
                ('termsOfService', self.api_tos),
                ('contact', OrderedDict([('name', self.api_contact_name)])),
                ('license', OrderedDict([('name', self.api_license_name)]))
            ])),
            ('host', self.api_host),
            ('basePath', self.api_basePath),
            ('schemes', self.api_schemes),
            ('paths', self.api_paths)
        ])

    def append_to_path(self, path, method, description):
        if self.api_paths is not None and path in self.api_paths.keys():
            self.api_paths[path].update(OrderedDict([(method.lower(), OrderedDict([("description", description)]))]))
        else:
            self.api_paths = OrderedDict([(path, OrderedDict([(method.lower(), OrderedDict([("description", description)]))]))])


state = SwaggerInfoBorg()


def output_swagger():
    return dumps(state.generate_object())


def swagger(route, method='GET', description=None):
    state.append_to_path(route, method, description)

    """ Let's behave like a wrapper """

    def decorator(f):
        return f

    return decorator
