from cloudmesh.common.Shell import Shell
from cloudmesh.common.StopWatch import StopWatch

import os
import shutil
import tarfile
import tempfile
import typing



"""
BUG: benchmark can be obtained with (this should also work just n a single file not just a dir
BUG: the lzma missing library bug should be caught and automatically the native method be used ... 

d = Data()
d.compress("dirname")
d.uncompress("dirname")
d.info("dirname")

StopWatch.benchmark()

Notes: I have forgotten if our Shell.run can do pipes. I remember one ofthem can actually do it

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


class Data:

    _OSBIN: typing.Final = {
            'xz': {
                'decompress': 'xzcat',
                'compress': 'xz',
                'suffix': 'xz',
                'level': 7
            },
            'bzip2': {
                'decompress': 'bzcat',
                'compress': 'bzip2',
                'suffix': 'bz2',
                'level': 9
            },
            'gz': {
                'decompress': 'zcat',
                'compress': 'gzip',
                'suffix': 'gz',
                'level': 9
            },
            'tar': {
                'command': 'tar',
                'switches': {
                    'gz': {
                        'compress': 'zcf',
                        'decompress': 'zxf',
                        'suffix': 'tar.gz'
                    },
                    'bzip': {
                        'compress': 'jcf',
                        'decompress': 'jxf',
                        'suffix': 'tar.bz2'
                    },
                    'xz': {
                        'compress': 'Jcf',
                        'decompress': 'Jxf',
                        'suffix': 'tar.xz'
                    },
                    'none': {
                        'compress': 'cf',
                        'decompress': 'xf',
                        'suffix': 'tar'
                    }
                }
            }
        }

    def __init__(self,
                 algorithm: str = "xz",
                 dryrun: bool = False,
                 force: bool = True,
                 tag: str = "",
                 *args,
                 **kwargs):

        # Test if native can be used.  If tar is missing, fall back to
        # native python method.
        self._native_tar = self._test_os_bin('tar') or self._test_os_bin('tar.exe')

        # Establish instance-level configuration settings
        self.config = {
            'algorithm': 'xz' if algorithm is None else algorithm,
            'dryrun': dryrun,
            'force': force,
            'tag': tag,
            'native': self._native_tar
        }
        self.config.update({'args': args,
                            'kwargs': kwargs})

        if tag is None:
            self.tag = ""
        else:
            self.tag = " " + tag

        # Setup native commands for future usage
        self.TAPE = self._OSBIN['tar']['command']
        self.COMPRESS = f"tar -{self._OSBIN['tar']['switches'][self.config['algorithm']]['compress']}"
        self.UNCOMPRESS = f"tar -{self._OSBIN['tar']['switches'][self.config['algorithm']]['decompress']}"
        self.ending = f"tar -{self._OSBIN['tar']['switches'][self.config['algorithm']]['suffix']}"

    def benchmark(self):
        StopWatch.benchmark()

    @staticmethod
    def _start(kind, location, tag):
        name = location.replace("/", "-")
        StopWatch.start(f"{kind}{tag} {name}")

    @staticmethod
    def _stop(kind, location, tag):
        name = location.replace("/", "-")
        StopWatch.stop(f"{kind}{tag} {name}")

    def _run(self, command):
        if self.config['dryrun']:
            r = command
            print(command)
        else:
            r = Shell.run(command)
        return r

    @staticmethod
    def info(source):
        """
        prints out information about the directory and if available the
        compressed file all types will be probed (xz, gz, bzip2)

        :param source: file or directory
        :return: str
        """
        r = Shell.run(f"du -s -h {source}")
        return r

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
        if os.path.isdir(source):
            self.compress_dir(source, destination, level)
        else:
            self.compress_file(source, destination)

    def compress_dir(self, source: str, destination: str = None, level: int = 5):
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
        """Compress an archive
        please convert to previous looking docstring


        Args:
            source(str): the path to the source file to compress
            destination(str): the path to write the compressed file to
            level(int): index for compression level (1-9, where 1 is the least
                and 9 is the most)

        Returns:
            None: method provides no feedback on operation.
        """
        # select native method
        if self._native_tar:
            self._os_compress_dir(source, destination=destination)
        else:
            # try python method first, but if lzm library is missing, use native method
            # TODO: source can be a file or a directory, so the method here seems incomplete as it
            #  does not capture that it can just be a file
            try:
                self._python_compress_dir(source, destination=destination, level=level)
            except tarfile.CompressionError:
                self._os_compress_dir(source, destination=destination)

    def compress_file(self, source: str, destination: str = None):
        """Compress a single file

        Creates a compressed archive from the source and writes it to the path
        destination.  Note, this method is designed to work on a single-file only,
        and is designed to work with self.tape.

        Args:
            source(str): the path to the source file to compress
            destination(str): the path to write the compressed file to.

        Returns:
            str: the path to the compressed file

        """
        if self.config['native']:
            name = self._os_compress_file(source, destination)
        else:
            name = self._python_compress_file(source, destination)
        return name

    def _os_compress_dir(self, location: str, destination: str):
        """Use os recursive compression

        Archives all files located under directory and compresses their
        data in one step.

        Args:
            location(str): The directory to scan for files to archive and
                compress
            destination(str): The path to write the compressed archive to.

        Returns:
            str: The path to the archive file.
        """

        """
        Note we may want to do this isn one step using the -z flag to tar and specifying the flag to tar 
        so we do everything in one step. which ought to be faster
        :param location: 
        :return: 
        """
        name = location.replace("/", "-") if destination is None else destination
        self._start("compress", name, self.tag)
        # deal with if destination already exists
        command = f"{self.COMPRESS} {name} {location}"
        self._run(command)
        self._stop("compress", name, self.tag, )
        return name

    def _python_compress_dir(self,
                             source: str,
                             destination: str,
                             level: typing.Union[str, int] = None) -> tarfile.TarFile:
        """Use python recursive compression

        Uses built-in python libraries to recursively add and compress files
        into an archive.

        Args:
            source(str): The path to scan for files to include in the archive
            destination(str): the path to write the archive destination to.
            level(int): The level of compression to apply.  From 0 to 9, where
                0 is no compression and 9 is extreme compression.

        Returns:
            tarfile.TarFile: the tarfile object that was created.
        """

        taropts = self._tarfile_bootstrap(
            self.config['algorithm'],
            extract=False,
            level=level
        )
        with tarfile.open(destination, **taropts) as tf:
            tf.add(source, recursive=True)

        return tf

    def uncompress_expand(self,
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
        if destination is None:
            destination = "."
        else:
            destination = destination

        if not os.path.exists(destination):
            os.makedirs(destination, exist_ok=True)
        elif force:
            pass
        else:
            raise FileExistsError("Destination exists!")

        self._start("uncompress", self.tag, source)
        if self.config['native']:
            self._os_uncompress_expand(source, destination)
        else:
            self._python_uncompress_expand(source, destination)
        self._stop("uncompress", self.tag, source)
        return destination

    def _os_uncompress_expand(self, source: str, destination: str):
        """Uses OS decompression tools

        Uncompresses and expands archive to the specified path using the OS
        native tooling.

        Args:
            source(str): The source to decompress and expand.
            destination(str): The path to expand the archive into.

        Returns:
            str: the path that the archive was expanded into.
        """
        """
        Note we may want to do this isn one step using the -z flag to tar and specifying the flag to tar 
        so we do everything in one step. which ought to be faster
        :param location: 
        :return: 
        """
        command = f"{self.UNCOMPRESS} {source} -C {destination}"
        self._run(command)
        return destination

    def _python_uncompress_expand(self, source: str, destination: str = None):
        """Uses python's modules for decompression tools

        Uncompresses and expands archive to the specified path using pythons
        internal module tooling.

        Args:
            source(str): The source to decompress and expand.
            destination(str): The path to expand the archive into.

        Returns:
            str: the path that the archive was expanded into.
        """
        taropts = self._tarfile_bootstrap(
            self.config['algorithm'],
            extract=True
        )
        with tarfile.open(source, **taropts) as tf:
            tf.extractall(destination)
        return destination

    @staticmethod
    def _test_os_bin(cmd: str) -> bool:
        """Tests if a command is on the path

        Performs a simple check to see if the specified command is on the
        path and can be used.

        Args:
            cmd(str): the name of the command to check for

        Returns:
            bool: True if the command is on the path, otherwise False.
        """
        return shutil.which(cmd) is not None

    @staticmethod
    def _tarfile_bootstrap(algorithm: str = None,
                           extract: bool = False,
                           level: int = None) -> typing.Dict[str, typing.Union[str, int]]:
        """tarfile configuration method

        Unifies multiple tarfile configuration options across several
        algorithms.  This method is meant to generalize the construction
        of tarfile.Open objects.

        Args:
            algorithm(str): The name of the algorithm to prepare the tarfile
                command.
            extract(bool): Set to True to return configurations for extracting
                a tarfile.  Set to False to return configuration for creating
                a tarsource.
            level(int): Specifies the level of compression to use for a specific
                algorithm.

        Returns:
            dict[str, Union[str,int]]:
        """
        if extract:
            mode = 'r'
        else:
            mode = 'x'
        compression_create_types = {
            'xz': f'{mode}:xz',
            'gz': f'{mode}:gz',
            'bz2': f'{mode}:bz2',
            None: mode
        }
        tarops = {
            'mode': compression_create_types[algorithm],
        }

        if level is None:
            compress = 7
        else:
            compress = level

        if not extract:
            if algorithm in ('gz', 'bz2'):
                tarops.update(dict(compresslevel=compress))
            elif algorithm == 'xz':
                tarops.update(dict(preset=compress))
            else:
                pass

        return tarops
