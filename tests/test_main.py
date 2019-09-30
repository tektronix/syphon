"""tests.test_main.py

   Copyright Keithley Instruments, LLC.
   Licensed under MIT (https://github.com/tektronix/syphon/blob/master/LICENSE)

"""
import os
import sys
from typing import List

import pytest
from _pytest.capture import CaptureFixture, CaptureResult
from py._path.local import LocalPath
from sortedcontainers import SortedDict

import syphon
import syphon.__main__
import syphon.core.check
import syphon.schema

from . import get_data_path, rand_string
from .assert_utils import assert_captured_outerr, assert_matches_outerr

SCHEMA = SortedDict({"0": "Species", "1": "PetalColor"})


def _archive_args(archive_dir_fixture: LocalPath, one_to_one: bool = True) -> List[str]:
    if one_to_one:
        return [
            "syphon",
            "archive",
            os.path.join(get_data_path(), "iris-part-*-of-6.csv"),
            os.path.join(get_data_path(), "iris-part-*-of-6.meta"),
            str(archive_dir_fixture),
            "-m",
            ".meta",
        ]
    else:
        return [
            "syphon",
            "archive",
            os.path.join(get_data_path(), "iris-part-1-of-6.csv"),
            os.path.join(get_data_path(), "iris-part-1-of-6-meta-part-*-of-2.meta"),
            str(archive_dir_fixture),
            "-m",
            ".meta",
            "--one-to-many",
        ]


def _build_args(
    archive_dir_fixture: LocalPath, cache_file_fixture: LocalPath
) -> List[str]:
    return ["syphon", "build", str(archive_dir_fixture), str(cache_file_fixture)]


def _check_args(cache_file_fixture: LocalPath) -> List[str]:
    return ["syphon", "check", str(cache_file_fixture)]


def _init_args(archive_dir_fixture: LocalPath) -> List[str]:
    result: List[str] = ["syphon", "init", str(archive_dir_fixture)]
    result.extend(SCHEMA.values())
    return result


class TestMain(object):
    @staticmethod
    def test_archive_one_to_many(archive_dir: LocalPath):
        from glob import glob

        assert syphon.__main__.main(_init_args(archive_dir)) == 0
        assert syphon.__main__.main(_archive_args(archive_dir, one_to_one=False)) == 0
        assert len(glob(os.path.join(archive_dir, "**"), recursive=True)) > 1

    @staticmethod
    def test_archive_one_to_one(archive_dir: LocalPath):
        from glob import glob

        assert syphon.__main__.main(_init_args(archive_dir)) == 0
        assert syphon.__main__.main(_archive_args(archive_dir, one_to_one=True)) == 0
        assert len(glob(os.path.join(archive_dir, "**"), recursive=True)) > 1

    @staticmethod
    def test_archive_complains_when_hashfile_given_without_increment(
        capsys: CaptureFixture, tmpdir: LocalPath, archive_dir: LocalPath
    ):
        datafile: LocalPath = tmpdir.join(rand_string())
        datafile.write(rand_string())

        with pytest.raises(SystemExit):
            syphon.__main__.main(
                [
                    "syphon",
                    "archive",
                    str(datafile),
                    str(archive_dir),
                    "--hashfile",
                    rand_string(),
                ]
            )
        assert_captured_outerr(capsys.readouterr(), False, True)

    @staticmethod
    def test_archive_complains_when_data_file_does_not_exist(
        capsys: CaptureFixture, archive_dir: LocalPath
    ):
        assert (
            syphon.__main__.main(["syphon", "archive", rand_string(), str(archive_dir)])
            == 2
        )
        assert_captured_outerr(capsys.readouterr(), False, True)

    @staticmethod
    @pytest.mark.parametrize("specify_hashfile", [True, False])
    def test_build(
        archive_dir: LocalPath,
        cache_file: LocalPath,
        hash_file: LocalPath,
        specify_hashfile: bool,
    ):
        assert not os.path.exists(cache_file)
        assert syphon.__main__.main(_init_args(archive_dir)) == 0
        assert syphon.__main__.main(_archive_args(archive_dir)) == 0

        arguments = _build_args(archive_dir, cache_file)
        if specify_hashfile:
            arguments.append(str(hash_file))

        assert syphon.__main__.main(arguments) == 0
        assert os.path.exists(cache_file)
        assert os.path.exists(
            hash_file
            if specify_hashfile
            else cache_file.dirpath(syphon.core.check.DEFAULT_FILE)
        )
        # If we're using our own hash file, then the default should not be created.
        if specify_hashfile:
            assert not os.path.exists(
                cache_file.dirpath(syphon.core.check.DEFAULT_FILE)
            )
        assert cache_file.size() > 0

    @staticmethod
    def test_build_no_hash(archive_dir: LocalPath, cache_file: LocalPath):
        assert not os.path.exists(cache_file)
        assert syphon.__main__.main(_init_args(archive_dir)) == 0
        assert syphon.__main__.main(_archive_args(archive_dir)) == 0

        arguments = _build_args(archive_dir, cache_file)
        arguments.append("--no-hash")

        assert syphon.__main__.main(arguments) == 0
        assert os.path.exists(cache_file)
        assert not os.path.exists(cache_file.dirpath(syphon.core.check.DEFAULT_FILE))
        assert cache_file.size() > 0

    @staticmethod
    def test_check(archive_dir: LocalPath, cache_file: LocalPath):
        assert syphon.__main__.main(_init_args(archive_dir)) == 0
        assert syphon.__main__.main(_archive_args(archive_dir)) == 0
        assert syphon.__main__.main(_build_args(archive_dir, cache_file)) == 0
        assert syphon.__main__.main(_check_args(cache_file)) == 0

    @staticmethod
    def test_init(archive_dir: LocalPath):
        assert len(archive_dir.listdir()) == 0
        assert syphon.__main__.main(_init_args(archive_dir)) == 0
        assert SCHEMA == syphon.schema.load(
            os.path.join(archive_dir, syphon.schema.DEFAULT_FILE)
        )

    @staticmethod
    def test_version(capsys: CaptureFixture):
        assert syphon.__main__.main(["syphon", "--version"]) == 0

        output: CaptureResult = capsys.readouterr()
        assert_captured_outerr(output, True, False)
        assert_matches_outerr(output, [syphon.__version__], [])


class TestMainHelp(object):
    @staticmethod
    def test_argument_prints_full_help():
        # syphon.__main__:main is the entry point, so make sure it inherits sys.argv
        # (subprocess.Popen is used so main doesn't use our sys.argv).
        import subprocess

        proc = subprocess.Popen(
            [
                os.path.join(
                    os.environ["TOX_ENV_DIR"],
                    "Scripts" if sys.platform == "win32" else "bin",
                    "python.exe" if sys.platform == "win32" else "python",
                ),
                "-m",
                "syphon",
                "--help",
            ],
            stdout=subprocess.PIPE,
        )
        proc.wait()

        output: str
        output, _ = proc.communicate()

        assert proc.returncode == 0
        assert output.lower().startswith(b"usage:")
        assert output.find(bytes(syphon.__url__, "utf8")) != -1

    @staticmethod
    def test_no_args_prints_usage():
        # syphon.__main__:main is the entry point, so make sure it inherits sys.argv
        # (subprocess.Popen is used so main doesn't use our sys.argv).
        import subprocess

        proc = subprocess.Popen(
            [
                os.path.join(
                    os.environ["TOX_ENV_DIR"],
                    "Scripts" if sys.platform == "win32" else "bin",
                    "python.exe" if sys.platform == "win32" else "python",
                ),
                "-m",
                "syphon",
            ],
            stdout=subprocess.PIPE,
        )
        proc.wait()

        output: str
        output, _ = proc.communicate()

        assert proc.returncode == 1
        assert output.lower().startswith(b"usage:")
        # Only the full help output contains the project URL.
        assert output.find(bytes(syphon.__url__, "utf8")) == -1
