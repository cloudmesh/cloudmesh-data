from cloudmesh.common.Shell import Shell
from cloudmesh.common.StopWatch import StopWatch

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

    def __init__(self, algorithm="xz", dryrun=False, force=True, tag=None):
        if tag is None:
            self.tag = ""
        else:
            self.tag = " " + tag
        self.algorithm = algorithm
        self.dryrun = dryrun
        self.force = True # if tru forces overwrite on creation, please implement
        if algorithm == "xz":
            self.COMPRESS = "xz"
            self.UNCOMPRESS = "xzcat"
            self.ending = "xz"
        elif algorithm == "bzip2":
            self.COMPRESS = "bzip2"
            self.UNCOMPRESS = "bzcat"
            self.ending = "bz"
        else:
            self.COMPRESS = "gzip"
            self.UNCOMPRESS = "zcat"
            self.ending = "gz"

    def _start(self, kind, location, tag):
        name = location.replace("/", "-")
        StopWatch.start(f"{kind}{tag} {name}")

    def _stop(self, kind, location, tag):
        name = location.replace("/", "-")
        StopWatch.stop(f"{kind}{tag} {name}")

    def _run(self, command):
        if self.dryrun:
            print(command)
        else:
            r = Shell.run(command)

    def info(self, location):
        """
        prints out information about the directory and if available the compressed file
        all types will be probed (xz, gz, bzip2)

        :param location: file or directory
        :return: str
        """
        r = ""
        return r
        
    def compress(self, location):
        """
        compresses the file or directory at the given location

        :param location:
        :return:
        """

        """
        Note we may want to do this isn one step using the -z flag to tar and specifying the flag to tar 
        so we do everything in one step. which ought to be faster
        :param location: 
        :return: 
        """
        name = location.replace("/", "-")
        self._start("compress", self.tag,name)
        if self.COMPRESS:
            # deal with if destination already exists
            command = "tar czf {location}"
            self._run(command)
        else:
            command = f"tar cvf {location}"
            self._run(command)
            command = f"{self.COMPRESS} {location}.tar"
            self._run(command)
        self._stop("compress", self.tag, name)

    def uncompress(self, location):
        """
        compresses the file or directory at the given location

        :param location:
        :return:
        """
        """
        Note we may want to do this isn one step using the -z flag to tar and specifying the flag to tar 
        so we do everything in one step. which ought to be faster
        :param location: 
        :return: 
        """
        self._stop("uncompress", self.tag, location)
        if self.COMPRESS:
            # deal with if destination already exists
            command = "tar czf {location}"
            self._run(command)
        else:
            command = f"{self.COMPRESS} -x {location}.tar"
            self._run(command)
            command = f"tar xf {location}"
            self._run(command)
        self._stop("compress", self.tag, location)


