from collections import OrderedDict

__author__ = 'Johannes'

# noinspection PyPackageRequirements
from bson.json_util import dumps


def to_swagger_type(input_type):
    if input_type == "string":
        return OrderedDict([('type', 'string')])

    if input_type == "int":
        return OrderedDict([
            ('type', 'integer'),
            ('format', 'int32')
        ])


class SwaggerInfoBorg:
    def __init__(self):
        self.api_version = '1.0.0'
        self.api_title = "Swagger Petstore"
        self.api_description = "A sample API that uses a petstore as an example to demonstrate features in the swagger-2.0 specification"
        self.api_contact_name = "Swagger API Team"
        self.api_tos = "http://swagger.io/terms/"
        self.api_license_name = "MIT"
        self.api_host = "petstore.swagger.io"
        self.api_base_path = "/api"
        self.api_schemes = ["http"]
        self.api_paths = None
        self.api_definitions = OrderedDict()

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
            ('basePath', self.api_base_path),
            ('schemes', self.api_schemes),
            ('paths', self.api_paths),
            ('definitions', self.api_definitions)
        ])

    def append_to_definitions(self, class_name, cls):
        param_properties = OrderedDict([
            (x, to_swagger_type(cls.__dict__[x]))
            for x in cls.__dict__.keys()
            if isinstance(cls.__dict__[x], str)
        ])

        param_schema = OrderedDict([
            ('type', 'object'),
            ('properties', param_properties)
        ])
        self.api_definitions.update(OrderedDict([(class_name, param_schema)]))

    def append_to_path(self, path, method, description, response, parameter):
        path_object = OrderedDict([(method.lower(), OrderedDict([("description", description)]))])

        if parameter is not None:
            class_name = type(parameter).__name__
            self.append_to_definitions(class_name, parameter)
            param_base = OrderedDict([
                ('name', 'input'), ('in', 'body'), ('required', True),
                ('schema', OrderedDict([('$ref', '#/definitions/' + class_name)]))
            ])
            path_object[method.lower()].update(OrderedDict([("parameters", [param_base])]))

        if response is not None:
            class_name = type(response).__name__
            self.append_to_definitions(class_name, response)
            response_schema = OrderedDict([('$ref', '#/definitions/' + class_name)])
            if hasattr(response, 'is_array') and response.is_array:
                response_schema = OrderedDict([
                    ('type', 'array'),
                    ('items', response_schema)
                ])

            response_base = OrderedDict([
                ("default", OrderedDict([
                    ('description', 'This is the description for default'),
                    ('schema', response_schema)
                ]))
            ])
            path_object[method.lower()].update(OrderedDict([("responses", response_base)]))

        if self.api_paths is not None and path in self.api_paths.keys():
            self.api_paths[path].update(path_object)
        elif self.api_paths is None:
            self.api_paths = OrderedDict([(path, path_object)])
        else:
            self.api_paths[path] = path_object


state = SwaggerInfoBorg()


def set_info(version, title, description, contact_name):
    state.api_version = version
    state.api_title = title
    state.api_description = description
    state.api_contact_name = contact_name


def set_legal(tos, licence):
    state.api_tos = tos
    state.api_license_name = licence


def set_host(host, base_path, schemes):
    state.api_host = host
    state.api_base_path = base_path
    state.api_schemes = schemes


def output_swagger():
    swagger_object = state.generate_object()
    return dumps(swagger_object)


def swagger(route, method='GET', description=None, response=None, param=None):
    state.append_to_path(route, method, description, response, param)

    """ Let's behave like a wrapper """

    def decorator(f):
        return f

    return decorator
