###############################################################
# npytest -v --capture=no  tests/test_data.py::Test_data.test_001_help
# pytest -v --capture=no  tests/test_data.py
# pytest -v tests/test_data.py
###############################################################

import os
import pytest
import hashlib
from testfixtures import compare
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING
from cloudmesh.data.create import ascii_file
from cloudmesh.data.create import random_file
from cloudmesh.data.command.data import DataCommand as data


@pytest.mark.incremental
class Test_data(object):

    def setup(self):
        self.size = "1GB"

    def test_001_help(self):
        HEADING()
        r = Shell.run("cms data")
        print(r)
        assert "Usage:" in r
        assert "data compress [--benchmark]" in r
        assert "ERROR: Could not execute the command." in r

    def test_002_create_files(self):
        HEADING()
        ascii_file(f"a_{self.size}.txt", self.size)
        random_file(f"r_{self.size}.txt", self.size)
        for r in [f"a_{self.size}.txt",
                  f"r_{self.size}.txt"]:
            size = os.stat(r).st_size
            print(size)

    #@pytest.mark.xfail(run=False, reason="shlex is unable to process wit do_data; maybe move to click?")
    def test_003_compress(self):
        HEADING()
        r = data.do_data([
                f" --source=r_{self.size}.txt",
                f" --destination=r_{self.size}.txt.xz"], None)

        a = data.do_data([
                f" --source=a_{self.size}.txt",
                f" --destination=a_{self.size}.txt.xz"], None)

        for fyle in [f"a_{self.size}.txt",
                     f"a_{self.size}.txt.xz",
                     f"r_{self.size}.txt",
                     f"r_{self.size}.txt.xz"]:
            r = os.stat(fyle).st_size
            print(r)

    def test_004_uncompress(self):
        HEADING()
        Shell.run("cms data uncompress"
                  f" --source=r_{self.size}.txt.xz"
                  f" --destination=r_uncompressed_{self.size}.txt")
        Shell.run("cms data uncompress"
                  f" --source=a_{self.size}.txt.xz"
                  f" --destination=a_uncompressed_{self.size}.txt")

    def test_005_integrity(self):
        HEADING()
        def create_hash(file):
            sha256 = hashlib.sha256()
            with open(file, 'rb') as f:
                buffer = f.read()
                sha256.update(buffer)
                return sha256.hexdigest()
        ascii_original = create_hash(f"a_{self.size}.txt")
        ascii_uncompressed = create_hash(f"a_uncompressed_{self.size}.txt")
        random_original = create_hash(f"r_{self.size}.txt")
        random_uncompressed = create_hash(f"r_uncompressed_{self.size}.txt")
        compare(ascii_original, ascii_uncompressed)
        compare(random_original, random_uncompressed)

    def test_100_cleanup(self):
        HEADING()
        os.system("rm *.txt *.txt.xz")
