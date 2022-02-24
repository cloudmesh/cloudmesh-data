from cloudmesh.common.Shell import Shell
from cloudmesh.common.StopWatch import StopWatch

import bz2
import dataclasses
import gzip
import os
import shutil
import sys
import tarfile
import typing

try:
    import lzma
except ImportError as e:
    print("WARNING: System not built with LZMA support, system will only support native calls",
          file=sys.stderr)

"""
BUG: benchmark can be obtained with (this should also work just n a single file not just a dir
BUG: the lzma missing library bug should be caught and automatically the native method be used ... 

d = Data()
d.compress("dirname")
d.uncompress("dirname")
d.info("dirname")

StopWatch.benchmark()

Notes: I have forgotten if our Shell.run can do pipes. I remember one of them can actually do it

DIR could also be a single file

compress:

tar c DIR | xz > DIR.tar.xz
tar c DIR | gzip > DIR.tar.gz
tar c DIR | bzip2 > DIR.tar.gz

Decompressing:

xzcat DIR.tar.xz | tar x
bzcat DIR.tar.bz2 | tar x
tar xf DIR.tar.gz    

"""

@dataclasses.dataclass
class CompressExtensions:
    gz = ('.gz',)
    bz2 = ('.bz2',)
    xz = ('.xz',)
    tar = ('.tar',)
    targz = ('.tar.gz', '.tgz')
    tarbz2 = ('.tar.bz2', '.tbz2')
    tarxz = ('.tar.xz', '.txz')



    @staticmethod
    def detect(path):
        DEBUG = True
        ret = None
        if path.endswith(CompressExtensions.targz):
            ret = 'targz'
        elif path.endswith(CompressExtensions.tarbz2):
            ret = 'tarbz2'
        elif path.endswith(CompressExtensions.tarxz):
            ret = 'tarxz'
        elif path.endswith(CompressExtensions.gz):
            ret = "gz"
        elif path.endswith(CompressExtensions.bz2):
            ret = 'bz2'
        elif path.endswith(CompressExtensions.xz):
            ret = 'xz'
        elif path.endswith(CompressExtensions.tar):
            ret = "tar"
        else:
            ret = None
        return ret


class Data:
    # kind = "xz"
    # if os.path.isdir("a")
    #    command = Data._COMMAND[kind]["dir"]["compress"].format(SOURCE="a", DESTINATION="a")
    # else:
    #    command = command = Data._COMMAND[kind]["file"]["compress"].format(SOURCE="a", DESTINATION="a")
    # self._run(command)

    # decompress
    # if "tar" in SOURCE:
    #    archive = "dir"
    # else:
    #    archive = "file"
    # source = SOURCE.split(".tar")[0]
    # command = Data._COMMAND[kind][archive]["decompress"].format(SOURCE=source)
    def __init__(self,
                 algorithm: str = "xz",
                 dryrun: bool = False,
                 force: bool = True,
                 tag: str = "",
                 *args,
                 **kwargs):

        # Establish instance-level configuration settings
        self._algo: typing.Final = 'xz' if algorithm is None else algorithm
        self._tag: typing.Final = "" if tag is None else f" {tag}"
        self._dryrun: typing.Final = dryrun
        self._force: typing.Final = force
        self.config = {
            'algorithm': self._algo,
            'dryrun': self._dryrun,
            'force': self._force,
            'tag': self._tag
        }
        self.config.update({'args': args,
                            'kwargs': kwargs})

    @staticmethod
    def benchmark():
        # setting it to tru so it looks better
        StopWatch.timer_status["command"] = True
        StopWatch.benchmark()

    @staticmethod
    def _start(kind, location, tag):
        name = location.replace("/", "-")
        StopWatch.start(f"{kind}{tag} {name}")

    @staticmethod
    def _stop(kind, location, tag):
        name = location.replace("/", "-")
        StopWatch.stop(f"{kind}{tag} {name}")

    def _run(self, command, driver=Shell.run):
        """CLI Command Runner with driver substitution.

        Runs `command` using the specified `driver` on the system's path.
        If the value of `self._dryrun` is set to true, the command does not
        run.

        Args:
            command: The command to run
            driver: A function which implements the execution of the passed
                command.  By default, uses `cloudmesh.common.Shell`.

        Returns:
            str: Either the output from the command's run, or returns the
                string of the command as it was passed.
        """
        if self._dryrun:
            r = command
        else:
            r = driver(command)
        return r

    @staticmethod
    def get_info(source, binary=False):
        """
        prints out information about the directory and if available the
        compressed file all types will be probed (xz, gz, bzip2)

        :param source: file or directory
        :return: str
        """
        if not binary:
            return Shell.run(f"du -sh {source}").strip().split()[0]
        else:
            return Shell.run(f"du -sb {source}").strip().split()[0]

    def compress(self, source: str, destination: str = None, level: int = 5):
        """
        Public mechanism to compress a directory or single file using the
        instance configured algorithm in set in self.config['algorithm'].

        :param source:
        :type source:
        :param destination:
        :type destination:
        :param level:
        :type level:
        :return:
        :rtype:
        """
        # select native method
        if os.path.isdir(source):
            compress_type = "directory"
        else:
            compress_type = "file"

        compress_level = 5 if level is None else level
        args = dict(source=source,
                    destination=destination,
                    level=compress_level,
                    type_=compress_type)

        self._compress(**args)

    def _compress(self, *args, **kwargs):
        """Compress method to be inherited with alternate implementations

        This is a stub method that should be overridden by an implementation
        class.  For calling compress, use the `Data.compress()` function.

        Args:
            *args(typing.Any): Arguments for implementation class
            **kwargs(typing.Any): keyword arguments for implementation class

        Returns:
            typing.Any: Deferred to implementation class.

        Raises:
            RuntimeError: Cautions the user that they are using a method
            that must be implemented for the class.
        """
        raise RuntimeError("No compress method implemented.")

    def uncompress(self,
                   source: str,
                   destination: str = None,
                   force: bool = False) -> str:
        """General purpose decompression command

        Decompresses a compressed tar source using the instance's specified
        algorithm.

        Args:
            source(str): The path to the compressed archive file
            destination(str): The path to expand the archive into.  If not specified,
                the current directory will be used (e.g. ".")
            force(bool): disables FileExistsError if path already exists.

        Returns:
            str: the path to where the archive was expanded.

        """
        type_ = "directory" if source.endswith('.tar') else "file"

        command = dict(source=source,
                       destination=destination,
                       type_=type_,
                       force=force)

        self._uncompress(**command)

    def _uncompress(self, *args, **kwargs):
        """Uncompress method to be inherited with alternate implementations

        This is a stub method that should be overridden by an implementation
        class.  For calling compress, use the `Data.uncompress()` function.

        Args:
            *args(typing.Any): Arguments for implementation class
            **kwargs(typing.Any): keyword arguments for implementation class

        Returns:
            typing.Any: Deferred to implementation class.

        Raises:
            RuntimeError: Cautions the user that they are using a method
            that must be implemented for the class.
        """
        raise RuntimeError("No uncompress method implemented.")


class NativeData(Data):
    cmds: typing.Final = {
        'gz': {
            'cmds': 'gzip zcat'.split(),
            'compress': 'gzip -{LEVEL} {SOURCE} -c > {DESTINATION}',
            'uncompress': 'zcat {SOURCE} > {DESTINATION}',
            'level': 7
        },
        'bz2': {
            'cmds': 'bzip2 bzcat'.split(),
            'compress': 'bzip2 -{LEVEL} {SOURCE} -c > {DESTINATION}',
            'uncompress': 'bzcat {SOURCE} > {DESTINATION}',
            'level': 5
        },
        'xz': {
            'cmds': 'xz xzcat'.split(),
            'compress': 'xz {SOURCE} -c > {DESTINATION}',
            'uncompress': 'xzcat {SOURCE} > {DESTINATION}',
            'level': 5
        },
        "tar": {
            'cmds': ('tar', ),
            'compress'   : 'tar -cf {DESTINATION} {SOURCE}',
            'uncompress' : 'tar -xf {SOURCE} -C {DESTINATION}',
        },
        'targz': {
            'cmds': ('tar', ),
            'compress': 'tar -zcf {DESTINATION} {SOURCE}',
            'uncompress': 'tar -zxf {SOURCE} -C {DESTINATION}',
        },
        'tarbz2': {
            'cmds': ('tar', ),
            'compress': 'tar -jcf {DESTINATION} {SOURCE}',
            'uncompress'  : 'tar -jxf {SOURCE} -C {DESTINATION}',
        },
        'tarxz': {
            'cmds': ('tar', ),
            'compress': 'tar -Jcf {DESTINATION} {SOURCE}',
            'uncompress'  : 'tar -Jxf {SOURCE} -C {DESTINATION}',
        }
    }

    def __init__(self, *args, **kwargs):
        """Native compression data implementation that uses OS tooling on the path.

        This is an implementation of `cloudmesh.data.Data` that provides the
        `_compress` and `_uncompress` implementations using tools typically
        provided in a shell-like environment.  The class has a saftey mechanism
        that detects if the necessary tools are present on the system path, and
        if they are not, will raise a `RuntimeError`.

        """
        cli_tools = self.cmds[kwargs['algorithm']]['cmds']
        for tool in cli_tools:
            if not shutil.which(tool):
                raise RuntimeError(f"Missing native command toolchain {tool}")
        super().__init__(*args, **kwargs)

    def _compress(self,
                  source: str,
                  destination: str,
                  type_: str,
                  level: typing.Union[str, int] = None) -> str:
        """Use os recursive compression

        Archives all files located under directory and compresses their
        data in one step.

        Args:
            source(str): The directory to scan for files to archive and
                compress
            destination(str): The path to write the compressed archive to.
            type_(str): Does nothing in this implementation, but is made
                available to match inheriting signature.
            level(typing.Union[str,int]): Specifies the level of compression
                to apply (more accurately, it sets the block size used when
                building the compression dictionary).

        Returns:
            str: The path to the archive file.
        """
        name = source.replace("/", "-") if destination is None else destination

        command = self.cmds[self._algo]['compress'].format(
            SOURCE=source,
            DESTINATION=destination,
            LEVEL=level
            )
        self._start("compress", name, self._tag)
        self._run(command)
        self._stop("compress", name, self._tag, )
        return destination

    def _uncompress(self,
                    source: str,
                    destination: str,
                    type_: str,
                    force: bool):
        """Uses OS decompression tools

        Uncompresses and expands archive to the specified path using the OS
        native tooling.

        Args:
            source(str): The source to decompress and expand.
            destination(str): The path to expand the archive into.
            type_(str): Does nothing in this implementation.  Parameter provided
                to match the calling signature
            force(bool): If True, the uncompress method will override any
                existing files.  If False, if the destination already exists,
                it will raise an exception.  NOT IMPLEMENTED.

        Returns:
            str: the path that the archive was expanded into.

        Raises:

        """
        if not self._algo == 'xz':
            os.makedirs(destination, exist_ok=True)
        command = self.cmds[self._algo]['uncompress'].format(
            SOURCE=source,
            DESTINATION=destination
        )
        self._run(command)
        return destination


class PythonData(Data):

    def __init__(self, *args, **kwargs):
        """Python compression implementation that uses python libraries part of the standard lib.

        This is an implementation of `cloudmesh.data.Data` that provides the
        `_compress` and `_uncompress` implementations using tools typically
        implemented in the pythons standard library.
        """
        super().__init__(*args, **kwargs)

    def _uncompress(self,
                    source: str,
                    destination: str = None,
                    force: bool = False,
                    type_: str = None):
        """Uses python's modules for decompression tools

        Uncompresses and expands archive to the specified path using pythons
        internal module tooling.

        Args:
            source(str): The source to decompress and expand.
            destination(str): The path to expand the archive into.
            force(bool): If True, then if the destination exists the file will
                be overridden. (NOT IMPLEMENTED).
            type_(str): Specifies the final type of the destination parameter.
                 One of "directory" or "file".

        Returns:
            str: the path that the archive was expanded into.
        """
        if type_ == "directory":
            taropts = self._tarfile_bootstrap(

                extract=True
            )
            with tarfile.open(source, **taropts) as tf:
                tf.extractall(destination)
        else:
            if self._algo == "lzma":
                with lzma.open(f"{source}", "rb") as f:
                    with open(destination, 'wb') as out:
                        shutil.copyfileobj(f, out)
            elif self._algo == 'gz':
                with gzip.open(f"{source}", "rb") as f:
                    with open(destination, 'wb') as out:
                        shutil.copyfileobj(f, out)
            elif self._algo == 'bz2':
                with bz2.open(f"{source}", "rb") as f:
                    with open(destination, 'wb') as out:
                        shutil.copyfileobj(f, out)
        return destination

    def _compress(self,
                  source: str,
                  destination: str,
                  type_: str,
                  level: typing.Union[str, int] = None) -> str:
        """Use python recursive compression

        Uses built-in python libraries to recursively add and compress files
        into an archive.

        Args:
            source(str): The path to scan for files to include in the archive
            destination(str): the path to write the archive destination to.
            type_(str): Specifies the final type of the source parameter.
                 One of "directory" or "file".
            level(int): The level of compression to apply.  From 0 to 9, where
                0 is no compression and 9 is extreme compression.

        Returns:
            str: the path to the compressed file.
        """
        name = source.replace("/", "-") if destination is None else destination
        if type_ == "directory":
            taropts = self._tarfile_bootstrap(
                extract=False,
                level=level
            )
            self._start("compress", name, self._tag)
            with tarfile.open(destination, **taropts) as tf:
                tf.add(source, recursive=True)
            self._stop("compress", name, self._tag, )
        elif type_ == "file":
            self._start("compress", name, self._tag)
            with open(source, 'rb') as f:
                if self._algo == "lzma":
                    with lzma.open(f"{destination}", "wb") as zf:
                        shutil.copyfileobj(f, zf)
                elif self._algo == 'gz':
                    with gzip.open(f"{destination}", "wb") as zf:
                        shutil.copyfileobj(f, zf)
                elif self._algo == 'bz2':
                    with bz2.open(f"{destination}", "wb") as zf:
                        shutil.copyfileobj(f, zf)
            self._stop("compress", name, self._tag)
        else:
            raise RuntimeError(f"Invalid path type {type_}")
        return destination

    def _tarfile_bootstrap(self,
                           extract: bool = False,
                           level: int = None,) -> typing.Dict[str, typing.Union[str, int]]:
        """tarfile configuration method

        Unifies multiple tarfile configuration options across several
        algorithms.  This method is meant to generalize the construction
        of tarfile.Open objects.

        Args:
            extract(bool): Set to True to return configurations for extracting
                a tarfile.  Set to False to return configuration for creating
                a tarsource.
            level(int): Specifies the level of compression to use for a specific
                algorithm.

        Returns:
            dict[str, Union[str,int]]:
        """
        mode = 'r' if extract else 'x'
        compression_create_types = {
            'tarxz' : f'{mode}:xz',
            'targz' : f'{mode}:gz',
            'tarbz2': f'{mode}:bz2',
            'tar': f'{mode}:'
        }
        tarops = {
            'mode': compression_create_types[self._algo],
        }

        if level is None:
            compress = 5
        else:
            compress = level

        if not extract:
            if self._algo in ('targz', 'tarbz2'):
                tarops.update(dict(compresslevel=compress))
            elif self._algo == 'tarxz':
                tarops.update(dict(preset=compress))
            else:
                raise RuntimeError(f"Unsupported algorithm {self._algo}")
        return tarops
