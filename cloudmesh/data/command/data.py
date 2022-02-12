from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from pprint import pprint
from cloudmesh.common.debug import VERBOSE
from cloudmesh.shell.command import map_parameters

class DataCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_data(self, args, arguments):
        """
        ::

          Usage:
                data compress [--algorithm=KIND] LOCATION
                data uncompress LOCATION
                data info LOCATION

          Compresses the specified item. The default algorithm is xy, Alternative it gz.

          Arguments:
              LOCATION   a file or directory name

          Options:
              -h      help

        """

        # arguments.FILE = arguments['--file'] or None

        map_parameters(arguments, "file")

        VERBOSE(arguments)

        if arguments.compress:
            location = arguments.LOCATION
            algorithm = arguments.algorithm

            print("option a")

        elif arguments.list:
            print("option b")

        return ""
