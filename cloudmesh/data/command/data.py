import sys

from cloudmesh.common.util import path_expand
from cloudmesh.data.data import CompressExtensions
from cloudmesh.data.data import NativeData
from cloudmesh.data.data import PythonData
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters


class DataCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_data(self, args, arguments):
        """
        ::

          Usage:
                data compress [--benchmark] [--algorithm=KIND] [--level=N] --source=SOURCE [--destination=DESTINATION] [--dryrun]
                data uncompress [--benchmark] [--force] --source=SOURCE [--destination=DESTINATION] [--dryrun]
                data info --source=SOURCE

          Compresses the specified item. The default algorithm is xz, Alternative it gz.
          Example if destination in compress is not specified the destination will be set to
          SOURCE.tar.xz

          Arguments:
              SOURCE       the file source on which compress or uncompress is aplied
              DESTINATION  the destination file on which compress or uncompress is performed

          Options:
              -h                help
              --level=N         the level of compression to apply 0 (no compression) to 9 (extreme)
              --algorithm=KIND  the algorithm to use; gz, bzip2, xz
              --force           disables file overwrite protection [default: False].

          Description:
            TBD

        """

        # TODO: compress should be
        #     data compress [--benchmark] [--algorithm=KIND] [--level=N] --source=SOURCE... [--destination=DESTINATION]
        # TODO: as far as I can tell sepopts is not needed .... do not have two steps ...

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
                       "level",
                       "force",
                       "csv",
                       "dryrun")

        if arguments.algorithm:
            algorithm = arguments.algorithm
        else:
            if arguments.compress:
                algorithm = CompressExtensions.detect(arguments.destination)
            else:
                algorithm = CompressExtensions.detect(arguments.source)

            if algorithm is None:
                algorithm = 'xz'

        try:
            worker = NativeData(algorithm=algorithm, dryrun=arguments.dryrun)
        except RuntimeError as e:
            print(e, file=sys.stderr)
            worker = PythonData(algorithm=algorithm, dryrun=arguments.dryrun)

        if arguments.compress:
            arguments.source = path_expand(arguments.source)
            arguments.destination = path_expand(arguments.destination)

            worker.compress(source=arguments.source,
                            destination=arguments.destination,
                            level=arguments.level)
            if arguments.benchmark:
                worker.benchmark()

        elif arguments.uncompress:
            arguments.source = path_expand(arguments.source)
            arguments.destination = path_expand(arguments.destination)

            print("In uncompress")
            print(type(worker))
            worker.uncompress(
                source=arguments.source,
                destination=arguments.destination,
                force=arguments.force)
            if arguments.benchmark:
                worker.benchmark()

        elif arguments.info:
            arguments.source = path_expand(arguments.source)
            _info_dest = worker.get_info(arguments.source)
            print(_info_dest, arguments.source)

            try:
                source = arguments.source.rsplit(".", 1)[0]
                _info_source = worker.get_info(source)
                print(_info_source, source)

                s = _info_source.split()[0]
                d = _info_dest.split()[0]
                r = float(worker.get_info(source, binary=True)) / float(worker.get_info(arguments.source, binary=True))
                print(f"{r:.2f}")

            except Exception as e:
                print(e)

        return ""
