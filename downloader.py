from pytube import YouTube
import sys
from pprint import pprint
from time import sleep
import subprocess
from pathlib import Path

CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'


def show_progress_bar(stream, chunk, file_handle, bytes_remaining):
    print('stream: {}'.format(stream))
    print('file_handle: {}'.format(file_handle))
    print('bytes_remaining: {}'.format(bytes_remaining))
    print('', end='\r')
    sys.stdout.write(CURSOR_UP_ONE)
    sys.stdout.write(ERASE_LINE)
    sys.stdout.write(CURSOR_UP_ONE)
    sys.stdout.write(ERASE_LINE)

    # sys.stdout.flush()
    sleep(0.1)


def downloader(*args, **kwargs):
    # defaults to having youtube link
    args = sys.argv or ["", "https://www.youtube.com/watch?v=B7bqAsxee4I"]
    print(args)
    print(args[1:])
    for file in args[1:]:
        yt = YouTube(file)
        pprint(yt.streams.all())
        try:
            itag = int(input("Which stream do you want? (integer) "))
        except ValueError:
            print("you need to provide a number!")

        yt.register_on_progress_callback(show_progress_bar)

        # if no audio then download the first audio as well
        download_target = yt.streams.get_by_itag(itag)

        if not download_target.audio_codec:
            print("downloading video first......")
            # first download the video
            video_fp = Path(download_target.download())

            # then the first audio stream
            print("downloading audio as well!")
            audio_fp = Path(yt.streams.filter(only_audio=True).first().download(
                output_path=video_fp.parent,
                filename=video_fp.stem + "-audio"))

            # mix audio as well afterwards
            print("attempting to mix audio and video")
            # -y: global ie overwrite without asking
            # -i: input file
            # -r: set frame rate in fps
            # -filter:a create filtergraph
            # -c:a copy means copy audio streams
            # -c:v copy means copy video stream codec
            # -filter:a aresample=async=1 means resample audio to fit frame rates
            cmd = \
                'ffmpeg -y -i "{}"  -r {} -i "{}"  -c:a copy -c:v copy "{}"'.format(
                    audio_fp,
                    download_target.fps,
                    video_fp,
                    str(video_fp.parent / video_fp.stem) + "-output.mkv"
                )
            print("Command to be run: {}".format(cmd))
            subprocess.run(cmd, shell=True)  # "Muxing Done
            print('Muxing Done')
        else:
            print("downloading VIDEO ONLY")
            download_target.download()

    print("All done!")


if __name__ == '__main__':
    downloader()
