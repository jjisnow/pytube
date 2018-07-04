from pySmartDL import SmartDL

from pytube import YouTube
import sys
from pprint import pprint
from time import sleep
import subprocess
from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)


def downloader(*args, **kwargs):
    # defaults to having youtube link
    if len(sys.argv) == 1:
        link = input("Provide a youtube link [default is a 3 second link]: ") \
               or "https://www.youtube.com/watch?v=B7bqAsxee4I"

        args = [sys.argv[0], link]
    else:
        args = sys.argv

    print(args)

    # download each file
    for file in args[1:]:
        yt = YouTube(file)
        pprint(yt.streams.all())
        while True:
            try:
                itag = int(input("Which stream do you want? (integer): "))
                break
            except ValueError:
                logging.error("you need to provide a number!")

        download_target = yt.streams.get_by_itag(itag)

        if not download_target.audio_codec:
            logging.info("downloading video first......")
            logging.info("current directory: {}".format(Path.cwd()))
            logging.info("Downloading url: {}".format(download_target.url))

            video_fp = download_video(download_target)

            # then the first audio stream
            logging.info("downloading audio as well!")

            download_target = yt.streams.filter(only_audio=True).first()
            logging.info("Downloading url: {}".format(download_target.url))

            audio_fp = str(video_fp.parent / video_fp.stem) \
                       + "-audio" \
                       + Path(download_target.default_filename).suffix
            logging.info("Targeting destination: {}".format(audio_fp))
            obj = SmartDL(download_target.url, audio_fp)
            obj.start()
            audio_fp = Path(obj.get_dest())
            print("Final audio file: {}".format(audio_fp))

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
            subprocess.run(cmd, shell=True)
            logging.info("Final muxed file: {}".format(final_fp))
            logging.info('Muxing Done')
        else:
            logging.info("downloading VIDEO ONLY")
            download_video(download_target)

    print("All done!")

def download_video(download_target):
    video_fp = Path.cwd() / Path(download_target.default_filename)
    logging.info("Targeting destination: {}".format(video_fp))
    obj = SmartDL(download_target.url, str(video_fp), threads=3)
    obj.start()
    video_fp = Path(obj.get_dest())
    print("Final Video file: {}".format(video_fp))
    return video_fp


if __name__ == '__main__':
    import time
    start_time=time.time()
    downloader()
    print("--- {:.2f} seconds ---".format(time.time() - start_time))
