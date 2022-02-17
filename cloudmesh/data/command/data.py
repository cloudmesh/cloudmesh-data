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
                data compress [--benchmark] [--algorithm=KIND] [--level=N] [--native] [--sepopts] --source=SOURCE [--destination=DESTINATION]
                data uncompress [--benchmark] [--native] [--sepopts] [--force] [--] --source=SOURCE [--destination=DESTINATION]
                data info LOCATION

          Compresses the specified item. The default algorithm is xz, Alternative it gz.
          Example if destination in compress is not specifued the destination will be set to
          SOURCE.tar.xz

          Arguments:
              SOURCE       the file source on which compress or uncompree is aplied
              DESTINATION  the detination file on which compress or uncompress is performed

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


        """
            du -h -s data
            4.7G	data
            du -h -s data.tar.xz 
            7.4M	data.tar.xz
            compress  data.tar.xz | ok       | 70.286 | 70.286 | 2022-02-17 02:06:34
        """

        map_parameters(arguments,
                       "benchmark",
                       "algorithm",
                       "source",
                       "destination",
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

            worker.compress(source=arguments.source,
                            destination=arguments.destination,
                            level=arguments.level)
            if arguments.benchmark:
                worker.benchmark()

        elif arguments.uncompress:
            arguments.source = path_expand(arguments.source)
            arguments.destination = path_expand(arguments.destination)

            worker.uncompress_expand(
                source=arguments.source,
                destination=arguments.destination,
                force=arguments.force)
            if arguments.benchmark:
                worker.benchmark()

        return ""
