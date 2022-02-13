from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.common.debug import VERBOSE
from cloudmesh.shell.command import map_parameters
from cloudmesh.data.data import Data

import pprint

class DataCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_data(self, args, arguments):
        """
        ::

          Usage:
                data compress [--algorithm=kind --level=n --native --sepopts] <file> [--] <location>
                data uncompress [--native --sepopts --force] [--] <file> [<destination>]
                data info <location>
                data benchmark [--csv]

          Compresses the specified item. The default algorithm is xz, Alternative it gz.

          Arguments:
              file   a file or directory name to compress or decompress
              location  the compression algorithm to use


          Options:
              -h        help
              --level=n   the level of compression to apply 0 (no compression) to 9 (extreme)
              --algorithm the algorithm to use; gz, bzip2, xz
              --native    use the OS provided tar for extraction, otherwise use python
              --sepopts   perform archival and compression as seperate steps
              --force     disables file overwrite protection.

        """

        # arguments.FILE = arguments['--file'] or None

        map_parameters(arguments, "file")

        VERBOSE(arguments)

        worker = Data(algorithm=arguments['--algorithm'],
                      native=True if arguments['--native'] else False,
                      sep_opts=True if arguments['--sepopts'] else False)

        if arguments.compress:
            worker.compress(src=arguments['<location>'],
                            out=arguments['<file>'],
                            level=arguments['--level'])

            print("option compress")
        elif arguments.uncompress:
            worker.uncompress_expand(
                file=arguments["<file>"],
                path=arguments["<destination>"],
                force=True if arguments['--force'] else False)

        elif arguments.benchmark:
            if arguments["--csv"]:
                # only returns the csv lines in the benchmark
                raise NotImplementedError
            else:
                from cloudmesh.common.StopWatch import StopWatch
                StopWatch.benchmark()

        return ""
