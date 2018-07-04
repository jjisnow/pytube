from pySmartDL import SmartDL

from pytube import YouTube
import sys
from pprint import pprint
from time import sleep
import subprocess
from pathlib import Path
import logging

CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'

logging.basicConfig(level=logging.DEBUG)


def show_progress_bar(stream, chunk, file_handle, bytes_remaining):
    # print('stream: {}'.format(stream))
    # print('file_handle: {}'.format(file_handle))
    print('KBytes_remaining: {:,.1f} KB'.format(bytes_remaining / 1024))
    # print()
    # print('', end='\r')
    # sys.stdout.write(CURSOR_UP_ONE)
    # sys.stdout.write(ERASE_LINE)
    # sys.stdout.write(CURSOR_UP_ONE)
    # sys.stdout.write(ERASE_LINE)
    sys.stdout.flush()
    sleep(0.2)


def downloader(*args, **kwargs):
    # defaults to having youtube link
    if len(sys.argv) == 1:
        args = [sys.argv[0], "https://www.youtube.com/watch?v=B7bqAsxee4I"]
    else:
        args = sys.argv
    print(args)
    for file in args[1:]:
        yt = YouTube(file)
        pprint(yt.streams.all())
        try:
            itag = int(input("Which stream do you want? (integer) "))
        except ValueError:
            logging.error("you need to provide a number!")

        # for longer files, display some progress info
        yt.register_on_progress_callback(show_progress_bar)

        # if no audio then download the first audio as well
        download_target = yt.streams.get_by_itag(itag)

        if not download_target.audio_codec:
            logging.info("downloading video first......")
            # video_fp = Path(download_target.download())
            logging.info("current directory: {}".format(Path.cwd()))
            logging.info("Downloading url: {}".format(download_target.url))

            obj = SmartDL(download_target.url, str(Path.cwd()), fix_urls=False)
            obj.start()
            video_fp = Path(obj.get_dest())

            logging.info("Video file: {}".format(video_fp))

            # then the first audio stream
            logging.info("downloading audio as well!")
            # audio_fp = Path(yt.streams.filter(only_audio=True).first().download(
            #     output_path=video_fp.parent,
            #     filename=video_fp.stem + "-audio"))

            download_target = yt.streams.filter(only_audio=True).first()
            logging.info("Downloading url: {}".format(download_target.url))
            obj = SmartDL(download_target.url, str(Path.cwd() / Path("audio")))
            obj.start()
            audio_fp = Path(obj.get_dest())
            logging.info("Temporary audio file: {}".format(audio_fp))
            audio_fp = audio_fp.replace(
                str(audio_fp.parents[1] / audio_fp.stem) + "-audio"
                + str(audio_fp.suffix))

            logging.info("Final audio file: {}".format(audio_fp))

            # mix audio as well afterwards
            logging.info("attempting to mix audio and video")
            # -y: global ie overwrite without asking
            # -i: input file
            # -r: set frame rate in fps
            # -filter:a create filtergraph
            # -c:a copy means copy audio streams
            # -c:v copy means copy video stream codec
            # -filter:a aresample=async=1 means resample audio to fit frame rates
            final_fp = str(video_fp.parent / video_fp.stem) + "-output.mkv"
            cmd = \
                'ffmpeg -y -i "{}"  -r {} -i "{}"  -c:a copy -c:v copy "{}"'.format(
                    audio_fp,
                    download_target.fps,
                    video_fp,
                    final_fp
                )
            logging.info("Command to be run: {}".format(cmd))
            subprocess.run(cmd, shell=True)  # "Muxing Done
            logging.info("Final muxed file: {}".format(final_fp))
            logging.info('Muxing Done')
        else:
            logging.info("downloading VIDEO ONLY")
            download_target.download()

    print("All done!")


if __name__ == '__main__':
    downloader()
