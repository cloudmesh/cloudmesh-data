###############################################################
# npytest -v --capture=no  tests/test_data.py::Test_data.test_001_help
# pytest -v --capture=no  tests/test_data.py
# pytest -v tests/test_data.py
###############################################################

import os
import pytest
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING
from cloudmesh.data.create import ascii_file
from cloudmesh.data.create import random_file


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
        for command in [f"du -h a_{self.size}.txt",
                        f"du -h r_{self.size}.txt"]:
            r = Shell.run(command).strip()
            print(r)

    def test_003_compress(self):
        HEADING()
        r = Shell.run("cms data compress"
                      f" --source=r_{self.size}.txt"
                      f" --destination=r_{self.size}.txt.xz"
                      ).strip()
        r = Shell.run("cms data compress"
                      f" --source=a_{self.size}.txt"
                      f" --destination=a_{self.size}.txt.xz"
                      ).strip()
        for command in [f"du -h a_{self.size}.txt",
                        f"du -h a_{self.size}.txt.xz",
                        f"du -h r_{self.size}.txt",
                        f"du -h r_{self.size}.txt.xz"]:
            r = Shell.run(command).strip()
            print(r)

    def test_100_cleanup(self):
        HEADING()
        os.system("rm *.txt *.txt.xz")
