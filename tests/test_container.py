from unittest import TestCase

from application import ServiceContainer, ServiceDefinition

class Config(object):
    SOME_PARAMETER = 'HELLO'

config = Config()


class TestServiceContainer(TestCase):

    def test_service_with_no_parameter(self):
        container = ServiceContainer()
        container.bootstrap(config)
        container.add_service_definition('no_param', ServiceDefinition(ServiceWithNoParameters, []))
        requested_service = container.get('no_param')

        self.assertIsInstance(requested_service, ServiceWithNoParameters)

    def test_service_with_config_parameter(self):
        container = ServiceContainer()
        container.bootstrap(config)
        container.add_service_definition('conf_param',
                                         ServiceDefinition(
                                            ServiceWithConfigParameter,
                                            ['config.SOME_PARAMETER']
                                            )
                                         )
        requested_service = container.get('conf_param')

        self.assertIsInstance(requested_service, ServiceWithConfigParameter)
        self.assertEqual(requested_service.my_param, 'HELLO')

    def test_service_with_dependencies(self):
        container = ServiceContainer()
        container.bootstrap(config)

        container.add_service_definition('no_param', ServiceDefinition(ServiceWithNoParameters, []))
        container.add_service_definition('conf_param', ServiceDefinition(
                                                         ServiceWithConfigParameter,
                                                         ['config.SOME_PARAMETER']
                                                     )
                                         )

        container.add_service_definition(
            'mixed_param',
            ServiceDefinition(
                ServiceWithDependencies,
                [
                    'no_param',
                    'conf_param',
                    'config.SOME_PARAMETER'
                ]
            )
        )

        requested_service = container.get('mixed_param')

        self.assertIsInstance(requested_service, ServiceWithDependencies)

        self.assertIsInstance(requested_service.no_param, ServiceWithNoParameters)
        self.assertIsInstance(requested_service.conf_param, ServiceWithConfigParameter)
        self.assertEqual(requested_service.my_param, 'HELLO')


class ServiceWithDependencies:
    def __init__(self, no_param, conf_param, my_param):
        self.no_param = no_param
        self.conf_param = conf_param
        self.my_param = my_param


class ServiceWithNoParameters:
    pass


class ServiceWithConfigParameter:
    def __init__(self, my_param):
        self.my_param = my_param
