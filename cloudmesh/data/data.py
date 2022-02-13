from cloudmesh.common.Shell import Shell
from cloudmesh.common.StopWatch import StopWatch

import os
import shutil
import tarfile
import tempfile
import typing


"""
benchmark can be obtained with 

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
                 native: bool = False,
                 sep_opts: bool = False,
                 *args,
                 **kwargs):

        # Test if native can be used.  If tar is missing, fall back to
        # native python method.
        if ((self._test_os_bin('tar') or self._test_os_bin('tar.exe'))
                and native):
            self._native_tar = True
        else:
            self._native_tar = False

        # Establish instance-level configuration settings
        self.config = {
            'algorithm': 'xz' if algorithm is None else algorithm,
            'dryrun': dryrun,
            'force': force,
            'tag': tag,
            'sep_opts': sep_opts,
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
    def info(location):
        """
        prints out information about the directory and if available the
        compressed file all types will be probed (xz, gz, bzip2)

        :param location: file or directory
        :return: str
        """
        r = f"{location}"
        return r

    def compress(self, src: str, out: str = None, level: int = 5):
        """Compress an archive

        Public mechanism to compress a directory or single file using the
        instance configured algorithm in set in self.config['algorithm'].

        Args:
            src(str): the path to the source file to compress
            out(str): the path to write the compressed file to
            level(int): index for compression level (1-9, where 1 is the least
                and 9 is the most)

        Returns:
            None: method provides no feedback on operation.
        """
        if self.config['sep_opts']:
            with tempfile.TemporaryDirectory() as tempd:
                self.compress_file(
                    src=self.tape(os.path.join(tempd, out),
                                  filename=out),
                    out=out)
        else:
            if self._native_tar:
                self._os_compress_dir(src, out=out)
            else:
                self._python_compress_dir(src, out=out, level=level)

    def tape(self, location: str, filename: str = None):
        """Creates a tar file

        This method recursively collects files from the specified location
        and creates a single tape archive (tar) of the files without
        applying any compression.

        Args:
            location(str): the path to the directory or file to include into
                the tape archive.
            filename(str): the path to use when writing the tape archive file.

        Returns:
            str: The name of the outputted tape archive.

        """
        if self.config['native']:
            name = self._os_tape_dir(location, filename)
        else:
            name = self._python_tape_dir(location, filename)
        return name

    def compress_file(self, src: str, out: str = None):
        """Compress a single file

        Creates a compressed archive from the src and writes it to the path
        out.  Note, this method is designed to work on a single-file only,
        and is designed to work with self.tape.

        Args:
            src(str): the path to the source file to compress
            out(str): the path to write the compressed file to.

        Returns:
            str: the path to the compressed file

        """
        if self.config['native']:
            name = self._os_compress_file(src, out)
        else:
            name = self._python_compress_file(src, out)
        return name

    def _os_tape_dir(self, location, out):
        raise NotImplementedError("Code not implemented yet")

    def _os_compress_file(self, src, out):
        raise NotImplementedError("Code not implemented yet")

    def _python_tape_dir(self, location, out):
        raise NotImplementedError("Code not implemented yet")

    def _python_compress_file(self, file, out):
        raise NotImplementedError("Code not implemented yet")

    def _os_compress_dir(self, location: str, out: str):
        """Use os recursive compression

        Archives all files located under directory and compresses their
        data in one step.

        Args:
            location(str): The directory to scan for files to archive and
                compress
            out(str): The path to write the compressed archive to.

        Returns:
            str: The path to the archive file.
        """

        """
        Note we may want to do this isn one step using the -z flag to tar and specifying the flag to tar 
        so we do everything in one step. which ought to be faster
        :param location: 
        :return: 
        """
        name = location.replace("/", "-") if out is None else out
        self._start("compress", name, self.tag)
        # deal with if destination already exists
        command = f"{self.COMPRESS} {name} {location}"
        self._run(command)
        self._stop("compress", name, self.tag, )
        return name

    def _python_compress_dir(self,
                             location: str,
                             out: str,
                             level: typing.Union[str, int] = None) -> tarfile.TarFile:
        """Use python recursive compression

        Uses built-in python libraries to recursively add and compress files
        into an archive.

        Args:
            location(str): The path to scan for files to include in the archive
            out(str): the path to write the archive out to.
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
        with tarfile.open(out, **taropts) as tf:
            tf.add(location, recursive=True)

        return tf

    def uncompress_expand(self,
                          file: str,
                          path: str = None,
                          force: bool = False) -> str:
        """General purpose decompression command

        Decompresses a compressed tar file using the instance's specified
        algorithm.

        Args:
            file(str): The path to the compressed archive file
            path(str): The path to expand the archive into.  If not specified,
                the current directory will be used (e.g. ".")
            force(bool): disables FileExistsError if path already exists.

        Returns:
            str: the path to where the archive was expanded.

        """
        if path is None:
            out = "."
        else:
            out = path

        if not os.path.exists(out):
            os.makedirs(out, exist_ok=True)
        elif force:
            pass
        else:
            raise FileExistsError("Destination exists!")

        self._start("uncompress", self.tag, file)
        if self.config['native']:
            self._os_uncompress_expand(file, out)
        else:
            self._python_uncompress_expand(file, out)
        self._stop("uncompress", self.tag, file)
        return out

    def _os_uncompress_expand(self, file: str, path: str):
        """Uses OS decompression tools

        Uncompresses and expands archive to the specified path using the OS
        native tooling.

        Args:
            file(str): The file to decompress and expand.
            path(str): The path to expand the archive into.

        Returns:
            str: the path that the archive was expanded into.
        """
        """
        Note we may want to do this isn one step using the -z flag to tar and specifying the flag to tar 
        so we do everything in one step. which ought to be faster
        :param location: 
        :return: 
        """
        command = f"{self.UNCOMPRESS} {file} -C {path}"
        self._run(command)
        return path

    def _python_uncompress_expand(self, file: str, path: str = None):
        """Uses python's modules for decompression tools

        Uncompresses and expands archive to the specified path using pythons
        internal module tooling.

        Args:
            file(str): The file to decompress and expand.
            path(str): The path to expand the archive into.

        Returns:
            str: the path that the archive was expanded into.
        """
        taropts = self._tarfile_bootstrap(
            self.config['algorithm'],
            extract=True
        )
        with tarfile.open(file, **taropts) as tf:
            tf.extractall(path)
        return path

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
                a tarfile.
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
