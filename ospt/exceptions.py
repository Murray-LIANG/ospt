class ConnectionError(Exception):
    pass


class TimeoutError(Exception):
    pass


class NotEnoughResourcesToDeleteError(Exception):
    pass


class CountOfServersVolumesNotMatchError(Exception):
    pass


class MappingNotSupportedError(Exception):
    def __init__(self, mapping):
        self.message = ('Mapping {} is not supported. Only <N>:1 or 1:<N> are '
                        'supported.'.format(mapping))


class NotEnoughResourcesForMappingError(Exception):
    def __init__(self, existing, required):
        self.message = '{} of resources are not enough, {} are needed.'.format(
            existing, required)
