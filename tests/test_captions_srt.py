from pytube import YouTube
import pytest

@pytest.fixture
def setup():
    # Captioned video link
    yt = YouTube("https://www.youtube.com/watch?v=QRS8MkLhQmM")
    return yt

def test_captions_srt(setup):
    a = setup.captions.all()[2]
    print(a.generate_srt_captions())
