from ospt.commands import volumes, servers, host_access

CMD = [volumes.CreateVolume, volumes.DeleteVolume,
       servers.CreateServer, servers.DeleteServer,
       host_access.Attach, host_access.Detach]

CMD_DICT = {cmd.name: cmd for cmd in CMD}
