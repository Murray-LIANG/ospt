class OsptException(Exception):
    msg = ''

    def __init__(self, message, **kwargs):
        _msg = message if message else self.msg
        super(Exception, self).__init__(_msg.format(**kwargs))


class ConnectionError(OsptException):
    pass


class TimeoutError(OsptException):
    pass


class NotEnoughResourcesToDeleteError(OsptException):
    pass


class CountOfServersVolumesNotMatchError(OsptException):
    pass


class MappingNotSupportedError(OsptException):
    msg = ('Mapping {mapping} is not supported. Only <N>:1 or 1:<N> are '
           'supported.')


class NotEnoughResourcesForMappingError(OsptException):
    msg = '{existing} of resources are not enough, {required} are needed.'
