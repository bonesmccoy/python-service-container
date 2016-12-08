class ServiceDefinition:
    def __init__(self, init, constructor_arguments):
        self.callable = init
        self.constructor_arguments = constructor_arguments


class ServiceContainer:

    def __init__(self):
        self.config = None
        self.services = {}
        self.service_definitions = {}
        self.start_initialization = {}
        self.bootstrapped = False

    def bootstrap(self, config):
        self.config = config
        self.bootstrapped = True

    def add_service_definition(self, service_name, service_definition):
        self.service_definitions[service_name] = service_definition

    def get(self, service_name):
        if not self.bootstrapped:
            raise Exception('Application not bootstrapped')

        if service_name in self.services:
            return self.services[service_name]

        if service_name not in self.service_definitions:
            raise NotImplementedError('Service not defined')

        if service_name in self.start_initialization:
            raise CircularDependencyException("circular dependency for service {}".format(service_name))

        self.start_initialization[service_name] = True

        service_definition = self.service_definitions[service_name]
        arguments = []
        for argument_in_constructor in service_definition.constructor_arguments:
            if 'config.' in argument_in_constructor:
                try:
                    config_parameter = getattr(
                        self.config,
                        argument_in_constructor.replace('config.', '')
                        )
                except Exception:
                    raise ParameterNotFoundException(
                        'Parameter {} not found in config'.format(argument_in_constructor)
                    )
                arguments.append(config_parameter)
            else:
                service_parameter = self.get(argument_in_constructor)
                arguments.append(service_parameter)

        self.services[service_name] = service_definition.callable(*arguments)

        del self.start_initialization[service_name]

        return self.services[service_name]


application = ServiceContainer()


class CircularDependencyException(Exception):
    pass


class ParameterNotFoundException(Exception):
    pass

