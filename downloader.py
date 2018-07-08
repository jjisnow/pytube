import os

from pySmartDL import SmartDL

from pytube import YouTube
import sys
from pprint import pprint
import subprocess
from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)


def downloader(*args, **kwargs):
    # Use a provided link or the args provided
    if len(sys.argv) == 1:
        link = input("Provide a youtube link to download: ")

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

        if not download_target.includes_audio_track:
            logging.info("downloading video first......")
            logging.debug("current directory: {}".format(Path.cwd()))
            video_fp = download_file(download_target)

            # then the first audio stream
            logging.info("downloading audio as well!")

            download_target = yt.streams.filter(only_audio=True).first()
            audio_fp = download_file(download_target)

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
            logging.debug("Command to be run: {}".format(cmd))
            subprocess.run(cmd, shell=True)
            logging.info("Final muxed file: {}".format(final_fp))
            logging.info('Muxing Done')
        else:
            logging.info("downloading VIDEO ONLY")
            video_fp = download_file(download_target)

        logging.info("CLEANUP: deleting video file")
        # check for errors
        errors = os.remove(video_fp)
        if not errors:
            logging.info("Success!")
        else:
            logging.error("Error code detected: {}".format(errors))

        if audio_fp:
            logging.info("CLEANUP: deleting audio file")
            # check for errors
            errors = os.remove(audio_fp)
            if not errors:
                logging.info("Success!")
            else:
                logging.error("Error code detected: {}".format(errors))

    print("All done!")


def download_file(download_target):
    logging.info("Downloading url: {}".format(download_target.url))

    fp = Path.cwd() / Path(download_target.default_filename)
    # add '-audio' suffix if audio file
    if download_target.type == 'audio':
        fp = str(fp.parent / fp.stem) \
             + "-audio" \
             + Path(download_target.default_filename).suffix
    logging.debug("Targeting destination: {}".format(fp))

    # download the file
    obj = SmartDL(download_target.url, str(fp), threads=5)
    obj.start(blocking=False)
    while not obj.isFinished():
        logging.info("Speed: %s" % obj.get_speed(human=True))
        logging.debug("Already downloaded: %s" % obj.get_dl_size(human=True))
        logging.info("Eta: %s" % obj.get_eta(human=True))
        logging.debug("Progress: %d%%" % (obj.get_progress() * 100))
        logging.info("Progress bar: %s" % obj.get_progress_bar())
        logging.debug("Status: %s" % obj.get_status())
        logging.debug("\n" * 2 + "=" * 50 + "\n" * 2)
        time.sleep(2)
    fp = Path(obj.get_dest())

    logging.info("Final {} file: {}".format(download_target.type, fp))
    return fp


if __name__ == '__main__':
    import time

    start_time = time.time()
    downloader()
    print("--- {:.2f} seconds ---".format(time.time() - start_time))
