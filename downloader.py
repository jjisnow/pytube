""" Downloader of video website links.
Will download video and mux with audio, or audio only, or video with audio already

Usage:
  downloader.py [URL...] [--verbose | --quiet] [--itag value] [--lang string]

Arguments:
  URL   individual websites to download video from

Options:
  -h, --help          Show this screen
  -v, --verbose       Show verbose output
  -q, --quiet         Run quietly
  -i, --itag value    The stream to download
  -l, --lang string   The caption language to download (default: English)

"""

import os
import shutil
import sys
from pprint import pformat

from pySmartDL import SmartDL
import time
from pytube import YouTube
import subprocess
from pathlib import Path
import logging
from docopt import docopt
from tabulate import tabulate


def parse_streams(streams):
    # take yt.streams.all() and parse into a list of dictionaries for presentation

    final_list = []
    for stream in streams:
        stream = str(stream).strip('<>').replace('Stream: ', '').split(' ')
        stream_dict = {}
        for item in stream:
            a = item.split('=')
            k = a[0]
            v = a[1].strip('"')
            stream_dict[k] = v
        final_list.append(stream_dict)

    print(tabulate(final_list, headers="keys"))


def download_captions(yt, lang):
    i = None
    captions = list(enumerate(yt.captions.all()))
    captions_string = pformat(captions)
    logging.debug(f'captions available: {captions_string}')
    for index, c in captions:
        if lang in str(c):
            i = index
            break
    if i is None:
        logging.debug(f'No {lang} Captions found!')
        return None

    subt_fp = f'{yt.title}-captions.srt'
    if os.path.exists(subt_fp):
        logging.info(f'File {subt_fp} exists already!! Deleting')
        os.remove(subt_fp)
    with open(subt_fp, 'w', encoding='utf-8') as f:
        logging.debug(f'Writing {subt_fp}')
        lines = yt.captions.captions[i].generate_srt_captions()
        f.write(lines)
        return subt_fp


def mux_files(audio_fp, subt_fp, video_fp, videofps=None):
    # mix audio as well afterwards
    logging.info("attempting to mix audio and video")
    # -y: global ie overwrite without asking
    # -i: input file
    # -r: set frame rate in fps
    # -filter:a create filtergraph
    # -c:a copy means copy audio streams
    # -c:v copy means copy video stream codec
    # -c:s srt means copy subtitles as srt
    # -filter:a aresample=async=1 means resample audio to fit frame rates
    if video_fp:
        final_fp = video_fp
    elif audio_fp:
        final_fp = audio_fp
    else:
        logging.error("")

    final_fp = Path(str(final_fp.parent / final_fp.stem) + ".mkv")
    audio_fp_text = f'-i "{audio_fp}"' if audio_fp else ''
    videofps_text = f'-r {videofps}' if videofps else ''
    video_fp_text = f'-i "{video_fp}"' if video_fp else ''
    subt_fp = '' if subt_fp is None else f'-i "{subt_fp}"'
    subt_text = '-c:s srt' if subt_fp else ''

    cmd = f'ffmpeg -y {audio_fp_text} {videofps_text} {video_fp_text} {subt_fp} -c:a ' \
          f'copy ' \
          f'-c:v copy {subt_text} "{final_fp}"'
    logging.debug("Command to be run: {}".format(cmd))
    subprocess.run(cmd, shell=True)
    logging.info("Final muxed file: {}".format(final_fp))
    logging.info('Muxing Done')
    return final_fp


def get_itag(arguments):
    while True:
        if arguments['--itag']:
            itag = arguments['--itag']
            break
        try:
            itag = int(input("Which stream do you want? (specify itag): "))
            break
        except ValueError:
            logging.error("you need to provide a number!")
    return itag


def config_loggers(arguments, log_level):
    """ displays the supplied arguments to stdout before switching back to the stderr
    handler

    :param arguments:
    :param log_level:
    :return:
    """

    logging.basicConfig(level=log_level)
    logger = logging.getLogger()

    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setLevel(log_level)
    logger.addHandler(stdout_handler)

    root_handler = logger.handlers[0]
    root_handler.setLevel(log_level)
    logger.removeHandler(root_handler)

    logger.info("Supplied args: \n {}".format(arguments))
    logger.removeHandler(stdout_handler)
    logger.addHandler(root_handler)


def download_file(download_target):
    logging.info("Downloading itag: {}".format(download_target.itag))
    logging.info("Download url: {}".format(download_target.url))

    fp = Path.cwd() / Path(download_target.default_filename)
    # add '-audio' suffix if audio file
    if download_target.type == 'audio':
        fp = ''.join((str(fp.parent / fp.stem),
                      "-audio",
                      Path(download_target.default_filename).suffix
                      ))
    logging.debug("Targeting destination: {}".format(fp))

    # download the file
    obj = SmartDL(download_target.url, str(fp), threads=5, progress_bar=False)
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


def parse_arguments():
    arguments = docopt(__doc__, help=True)
    if arguments['--verbose']:
        log_level = logging.DEBUG
    elif arguments['--quiet']:
        log_level = logging.CRITICAL
    else:
        log_level = logging.INFO
    # Decide on subtitles to use
    if arguments['--lang']:
        lang = arguments['--lang']
    else:
        arguments['--lang'] = lang = 'English'


    return arguments, lang, log_level


def downloader():
    ''' main interface for downloader file
    '''

    arguments, lang, log_level = parse_arguments()
    config_loggers(arguments, log_level)

    # Use a provided link or the args provided
    if len(arguments['URL']) == 0:
        link = input("Provide a youtube link to download: ")
        arguments['URL'].append(link)

    logging.info("Final args: {}".format(arguments))

    start_time = time.time()
    for file in arguments['URL']:
        logging.debug("Parsing url: {}".format(file))
        yt = YouTube(file)
        parse_streams(yt.streams.all())

        itag = get_itag(arguments)
        download_target = yt.streams.get_by_itag(itag)

        logging.info("DOWNLOADING:")
        video_path = None
        audio_path = None
        subtitle_path = None
        videofps = None
        # note this 'includes_audio_track' only applies to video with audio included
        if not download_target.includes_audio_track:
            logging.info("downloading video first......")
            logging.debug("current directory: {}".format(Path.cwd()))
            video_path = download_file(download_target)
            videofps = download_target.fps

            # then the first audio stream
            logging.info("downloading audio as well!")
            audio_target = yt.streams.filter(only_audio=True).first()
            audio_path = download_file(audio_target)

            # consider downloading subtitles
            subtitle_path = download_captions(yt, lang)

            final_fp = mux_files(audio_path, subtitle_path, video_path, videofps)
        else:
            logging.info("downloading {} ONLY".format(download_target.type))
            if download_target.type == 'video':
                video_path = download_file(download_target)
                videofps = download_target.fps
                subtitle_path = download_captions(yt, lang)
                final_base = mux_files(audio_path, subtitle_path, video_path, videofps)

            elif download_target.type == 'audio':
                audio_target = download_target
                audio_path = download_file(audio_target)
                subtitle_path = download_captions(yt, lang)
                final_base = mux_files(audio_path, subtitle_path, video_path, videofps)

            else:
                logging.critical("unexpected file type: {}".format(download_target.type))
                return 1

            final_fp = "".join((str(final_base.parent / final_base.stem),
                                "-output",
                                final_base.suffix
                                ))
            logging.debug("Renaming file: {}".format(final_fp))
            shutil.move(final_base, final_fp)

        logging.info("CLEANUP:")
        for k, v in {'audio'    : audio_path,
                     'video'    : video_path,
                     'subtitles': subtitle_path}.items():
            if v:
                logging.info("CLEANUP: deleting {} file: {}".format(k, v))
                # check for errors
                errors = os.remove(v)
                if not errors:
                    logging.info("Success!")
                else:
                    logging.error("Error code detected: {}".format(errors))
            else:
                logging.debug('CLEANUP: no {} file detected'.format(k))

        logging.info("Final output file: {}".format(final_fp))

    print("All done!")
    print("--- {:.2f} seconds ---".format(time.time() - start_time))


if __name__ == '__main__':
    downloader()
