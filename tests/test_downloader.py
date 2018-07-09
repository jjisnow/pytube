# test files
import os
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def base_command():
    # uses a short 30s wildlife clip
    command = " ".join(("python",
                        "downloader.py",
                        "https://www.youtube.com/watch?v=5DP5I8Gd6wY",
                        "-v",
                        "-i"
                        ))
    return command


def test_audio(base_command):
    # test for audio file only
    downloaded_expected = Path("Short wildlife video clip HD-audio-output.webm")
    if downloaded_expected.is_file():
        os.remove(downloaded_expected)
    cmd = base_command + " 249"
    subprocess.run(cmd, shell=True)

    if all((downloaded_expected.is_file(),
            downloaded_expected.stat().st_size == 223709)):
        os.remove(downloaded_expected)
        assert True
    else:
        assert False


def test_video_only(base_command):
    # test for low quality video file muxing
    downloaded_expected = Path("Short wildlife video clip HD-output.mkv")
    if downloaded_expected.is_file():
        os.remove(downloaded_expected)
    cmd = base_command + " 278"
    subprocess.run(cmd, shell=True)

    if all((downloaded_expected.is_file(),
            downloaded_expected.stat().st_size == 843467)):
        os.remove(downloaded_expected)
        assert True
    else:
        assert False


def test_combined(base_command):
    # test for low quality video file muxing
    downloaded_expected = Path("Short wildlife video clip HD-output.3gpp")
    if downloaded_expected.is_file():
        os.remove(downloaded_expected)
    cmd = base_command + " 17"
    subprocess.run(cmd, shell=True)

    if all((downloaded_expected.is_file(),
            downloaded_expected.stat().st_size == 289422)):
        os.remove(downloaded_expected)
        assert True
    else:
        assert False


def test_hq_combined(base_command):
    # test for high quality combined video file
    downloaded_expected = Path("Short wildlife video clip HD-output.mkv")
    if downloaded_expected.is_file():
        os.remove(downloaded_expected)
    cmd = base_command + " 247"
    subprocess.run(cmd, shell=True)

    if all((downloaded_expected.is_file(),
            downloaded_expected.stat().st_size == 6832831)):
        os.remove(downloaded_expected)
        assert True
    else:
        assert False
