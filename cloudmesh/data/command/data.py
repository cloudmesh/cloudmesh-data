from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.common.debug import VERBOSE
from cloudmesh.shell.command import map_parameters
from cloudmesh.data.data import Data
from cloudmesh.common.util import path_expand

import pprint

class DataCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_data(self, args, arguments):
        """
        ::

          Usage:
                data compress [--benchmark] [--algorithm=KIND] [--level=N] [--native] [--sepopts] FILE [--] LOCATION
                data uncompress [--benchmark] [--native] [--sepopts] [--force] [--] FILE [DESTINATION]
                data info LOCATION

          Compresses the specified item. The default algorithm is xz, Alternative it gz.

          Arguments:
              FILE         a file or directory name to compress or decompress
              LOCATION     the compression algorithm to use
              DESTINATION  the destination where for the uncompression of the directory or file

          Options:
              -h                help
              --level=N         the level of compression to apply 0 (no compression) to 9 (extreme)
              --algorithm=KIND  the algorithm to use; gz, bzip2, xz [default: xz]
              --native          use the OS provided tar for extraction, otherwise use python [default: True]
              --sepopts         perform archival and compression as seperate steps [default: False]
              --force           disables file overwrite protection [default: False].

          Description:
            TBD

        """
        map_parameters(arguments,
                       "benchmark",
                       "algorithm",
                       "file",
                       "native",
                       "level",
                       "force",
                       "csv",
                       "sepopts")

        VERBOSE(arguments)

        worker = Data(algorithm=arguments.algorithm,
                      native=arguments.native,
                      sep_opts=arguments.sepopts)

        if arguments.compress:
            arguments.LOCATION = path_expand(arguments.LOCATION)
            arguments.FILE = path_expand(arguments.FILE)

            worker.compress(src=arguments.LOCATION,
                            out=arguments.FILE,
                            level=arguments.level)
            if arguments.benchmark:
                worker.benchmark()

        elif arguments.uncompress:
            arguments.FILE = path_expand(arguments.FILE)
            arguments.DESTINATION = path_expand(arguments.DESTINATION)

            worker.uncompress_expand(
                file=arguments.FILE,
                path=arguments.DESTINATION,
                force=arguments.force)
            if arguments.benchmark:
                worker.benchmark()

        return ""
