# test files
import math
import os
import subprocess
from pathlib import Path

import pytest

from pytube import downloader


@pytest.fixture()
def base_command():
    return ' '.join((
        "python",
        os.path.join("..", "pytube", "downloader.py"),
        "-v",
    ))


@pytest.fixture
def wildlife_clip(base_command):
    # uses a short 30s wildlife clip
    url = "https://www.youtube.com/watch?v=5DP5I8Gd6wY"

    # youtube close caption demo
    # TODO: reference size of videos downloaded for tests
    # url = "https://www.youtube.com/watch?v=QRS8MkLhQmM"

    # short video with non-safe filename defaults
    # url = "https://www.youtube.com/watch?v=BpaYqFd5S5c"

    command = " ".join((base_command,
                        url,
                        ))
    return command


@pytest.fixture
def captions(base_command):
    # youtube close caption demo
    url = "https://www.youtube.com/watch?v=QRS8MkLhQmM"

    command = " ".join((base_command,
                        url,
                        ))
    return command


def check_expected(base_command, downloaded_expected, itag, size_expected):
    if downloaded_expected.is_file():
        os.remove(downloaded_expected)
    cmd = base_command + f" -i {str(itag)}"
    subprocess.run(cmd, shell=True)
    if all((downloaded_expected.is_file(),
            math.isclose(downloaded_expected.stat().st_size, size_expected,
                         rel_tol=0.01))):
        os.remove(downloaded_expected)
        assert True
    else:
        print()
        assert False


@pytest.mark.parametrize("args, expected", [
    (('aria2c', 'ffmpeg', 'ffprobe'), None)
])
def test_downloader_check_requirements(args, expected):
    assert downloader.check_requirements(*args) == None


@pytest.mark.parametrize("args", [
    ('blah_not_executable',)
])
def test_downloader_check_requirements_bad(args):
    with pytest.raises(Exception):
        downloader.check_requirements(args)


def test_list(wildlife_clip):
    assert subprocess.run(wildlife_clip + " 1 -l", shell=True)


def test_audio(wildlife_clip):
    # test for audio file only
    downloaded_expected = Path(
        "Short wildlife video clip HD-audio-output.mkv")
    itag = 249
    size_expected = 224096
    check_expected(wildlife_clip, downloaded_expected, itag, size_expected)


def test_video_only(wildlife_clip):
    # test for low quality video file muxing
    downloaded_expected = Path("Short wildlife video clip HD-output.mkv")
    itag = 278
    size_expected = 843467
    check_expected(wildlife_clip, downloaded_expected, itag, size_expected)


def test_combined(wildlife_clip):
    # test for low quality video file download
    downloaded_expected = Path("Short wildlife video clip HD-output.mkv")
    itag = 17
    size_expected = 291297
    check_expected(wildlife_clip, downloaded_expected, itag, size_expected)


def test_hq_combined(wildlife_clip):
    # test for high quality combined video file
    downloaded_expected = Path("Short wildlife video clip HD-output.mkv")
    itag = 247
    size_expected = 6832831
    check_expected(wildlife_clip, downloaded_expected, itag, size_expected)


def test_audio_captions(captions):
    # test for audio file only
    base_command = captions
    downloaded_expected = Path(
        "YouTube Captions and Subtitles-audio-output.mkv")
    itag = 249
    size_expected = 550250
    check_expected(base_command, downloaded_expected, itag, size_expected)


def test_video_only_captions(captions):
    # test for low quality video file muxing
    base_command = captions
    downloaded_expected = Path(
        "YouTube Captions and Subtitles-output.mkv")
    itag = 278
    size_expected = 2603339
    check_expected(base_command, downloaded_expected, itag, size_expected)


def test_combined_captions(captions):
    # test for low quality video file muxing
    base_command = captions
    downloaded_expected = Path("YouTube Captions and Subtitles-output.mkv")
    if downloaded_expected.is_file():
        os.remove(downloaded_expected)
    itag = 17
    size_expected = 1016003
    check_expected(base_command, downloaded_expected, itag, size_expected)


def test_hq_mux(captions):
    # test for high quality combined video file
    base_command = captions
    downloaded_expected = Path("YouTube Captions and Subtitles-output.mkv")
    itag = 243
    size_expected = 4846884
    check_expected(base_command, downloaded_expected, itag, size_expected)


def test_non_safe_file_title(base_command):
    url = "https://www.youtube.com/watch?v=BpaYqFd5S5c"
    base_command = " ".join((base_command,
                             url,
                             ))
    itag = 278
    cmd = base_command + f" -i {str(itag)}"
    downloaded_expected = Path(
        'Adam Savages New One Day Builds T-Shirt!-output.mkv')
    if downloaded_expected.is_file():
        os.remove(downloaded_expected)
    exit_code = subprocess.run(cmd, shell=True)
    os.remove(downloaded_expected)
    assert exit_code.returncode == 0
