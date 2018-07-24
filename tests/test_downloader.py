# test files
import math
import os
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def base_command():
    # uses a short 30s wildlife clip
    url = "https://www.youtube.com/watch?v=5DP5I8Gd6wY"

    # youtube close caption demo
    # TODO: reference size of videos downloaded for tests
    # url = "https://www.youtube.com/watch?v=QRS8MkLhQmM"

    command = " ".join(("python",
                        os.path.join("..", "downloader.py"),
                        url,
                        "-v",
                        "-i"
                        ))
    return command


@pytest.fixture
def captions():
    # youtube close caption demo
    # TODO: reference size of videos downloaded for tests
    url = "https://www.youtube.com/watch?v=QRS8MkLhQmM"

    command = " ".join(("python",
                        os.path.join("..","downloader.py"),
                        url,
                        "-v",
                        "-i"
                        ))
    return command

def test_list(base_command):
    assert subprocess.run(base_command + " 1 -l", shell=True)


def test_audio(base_command):
    # test for audio file only
    downloaded_expected = Path("Short wildlife video clip HD-audio-output.mkv")
    if downloaded_expected.is_file():
        os.remove(downloaded_expected)
    cmd = base_command + " 249"
    subprocess.run(cmd, shell=True)
    size_expected = 224096
    if all((downloaded_expected.is_file(),
        math.isclose(downloaded_expected.stat().st_size, size_expected, rel_tol=0.01))):
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
    size_expected = 843467
    if all((downloaded_expected.is_file(),
        math.isclose(downloaded_expected.stat().st_size, size_expected, rel_tol=0.01))):
        os.remove(downloaded_expected)
        assert True
    else:
        assert False


def test_combined(base_command):
    # test for low quality video file download
    downloaded_expected = Path("Short wildlife video clip HD-output.mkv")
    if downloaded_expected.is_file():
        os.remove(downloaded_expected)
    cmd = base_command + " 17"
    subprocess.run(cmd, shell=True)
    size_expected = 291297
    if all((downloaded_expected.is_file(),
        math.isclose(downloaded_expected.stat().st_size, size_expected, rel_tol=0.01))):
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
    size_expected = 6832831
    if all((downloaded_expected.is_file(),
        math.isclose(downloaded_expected.stat().st_size, size_expected, rel_tol=0.01))):
        os.remove(downloaded_expected)
        assert True
    else:
        assert False


def test_audio_captions(captions):
    # test for audio file only
    downloaded_expected = Path("YouTube Captions and Subtitles-audio-output.mkv")
    if downloaded_expected.is_file():
        os.remove(downloaded_expected)
    cmd = captions + " 249"
    subprocess.run(cmd, shell=True)
    size_expected = 550250
    if all((downloaded_expected.is_file(),
        math.isclose(downloaded_expected.stat().st_size, size_expected, rel_tol=0.01))):
        os.remove(downloaded_expected)
        assert True
    else:
        assert False


def test_video_only_captions(captions):
    # test for low quality video file muxing
    downloaded_expected = Path("YouTube Captions and Subtitles-output.mkv")
    if downloaded_expected.is_file():
        os.remove(downloaded_expected)
    cmd = captions + " 278"
    subprocess.run(cmd, shell=True)
    size_expected = 2603339
    if all((downloaded_expected.is_file(),
        math.isclose(downloaded_expected.stat().st_size, size_expected, rel_tol=0.01))):
        os.remove(downloaded_expected)
        assert True
    else:
        assert False


def test_combined_captions(captions):
    # test for low quality video file muxing
    downloaded_expected = Path("YouTube Captions and Subtitles-output.mkv")
    if downloaded_expected.is_file():
        os.remove(downloaded_expected)
    cmd = captions + " 17"
    subprocess.run(cmd, shell=True)
    size_expected = 1016003
    if all((downloaded_expected.is_file(),
        math.isclose(downloaded_expected.stat().st_size, size_expected, rel_tol=0.01))):
        os.remove(downloaded_expected)
        assert True
    else:
        assert False


def test_hq_mux(captions):
    # test for high quality combined video file
    downloaded_expected = Path("YouTube Captions and Subtitles-output.mkv")
    if downloaded_expected.is_file():
        os.remove(downloaded_expected)
    cmd = captions + " 243"
    subprocess.run(cmd, shell=True)
    size_expected = 4846884
    if all((downloaded_expected.is_file(),
        math.isclose(downloaded_expected.stat().st_size, size_expected, rel_tol=0.01))):
        os.remove(downloaded_expected)
        assert True
    else:
        assert False
