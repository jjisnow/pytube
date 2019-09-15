""" Downloader of video website links.
Will download video and mux with audio, or audio only, or video with audio
already

Usage:
  downloader.py [URL...] [--verbose | --quiet] [--itag value] [--lang string]
  [--list] [--duration t] [--start s]

Arguments:
  URL   individual websites to download video from

Options:
  -h, --help          Show this screen
  -v, --verbose       Show verbose output
  -q, --quiet         Run quietly
  -i, --itag value    The stream to download
  --lang string       The caption language to download [default: English]
  -l, --list          List streams and exit
  -d, --duration t    Download t seconds
  -s, --start s       Start download at s seconds

"""
import datetime
import os
import shutil
from functools import wraps
from pprint import pformat

import time

import pysrt

from pytube import YouTube
import subprocess
from pathlib import Path
import logging
from docopt import docopt
from tabulate import tabulate


def timing(fn):
    '''Timing decorator for program'''

    @wraps(fn)
    def wrap(*args, **kw):
        time_start = time.time()
        result = fn(*args, **kw)
        time_end = time.time()
        print(f'function:{fn.__name__} args:[{args}, {kw}]'
              f'--- {time_end - time_start:2.2f} sec ---')
        return result

    return wrap


@timing
def downloader(*args, **kwargs):
    ''' main interface for downloader file
    '''

    arguments = parse_arguments()
    config_loggers(arguments)
    arguments = check_url(arguments)
    check_requirements('aria2c', 'ffmpeg')

    for file in arguments['URL']:
        logging.debug(f"Parsing url: {file}")
        yt = YouTube(file)
        parse_streams(yt.streams.all())
        if arguments['--list']:
            return 0

        itag = get_itag(arguments)
        target_stream = yt.streams.get_by_itag(itag)

        logging.info("DOWNLOADING:")
        video_path, audio_path, subtitle_path, videofps = [None] * 4
        if not target_stream.includes_audio_track:
            logging.info("downloading video first......")
            video_path = download_file(target_stream, duration=arguments['--duration'],
                                       start=arguments['--start'])
            videofps = target_stream.fps

            logging.info("downloading audio as well!")
            audio_target = yt.streams.filter(only_audio=True).first()
            audio_path = download_file(audio_target, duration=arguments['--duration'],
                                       start=arguments['--start'])

        else:
            logging.info(f"downloading {target_stream.type} ONLY")
            if target_stream.type == 'video':
                video_path = download_file(target_stream,
                                           duration=arguments['--duration'],
                                           start=arguments['--start'])
                videofps = target_stream.fps

            elif target_stream.type == 'audio':
                audio_target = target_stream
                audio_path = download_file(audio_target, duration=arguments['--duration'],
                                           start=arguments['--start'])

            else:
                logging.critical(
                    f"unexpected file type: {target_stream.type}")
                return 1

        # need to retime the captions if I'm to use them in shorter videos
        if not target_stream.type == 'audio':
            subtitle_path = download_captions(yt, lang=arguments['--lang'],
                                              duration=arguments['--duration'],
                                              start=arguments['--start'])

        # In the event only audio, create HQ mp3 or aac file
        if target_stream.type == 'audio':
            if (audio_path.suffix == '.webm' and target_stream.audio_codec == 'opus') \
                    or (
                    audio_path.suffix == '.mp4' and 'mp4' in target_stream.audio_codec):
                final_fp = make_mp3(audio_path)  # the default
                # final_fp = make_aac(audio_path)  # not supported by all platforms
                # final_fp = make_ogg(audio_path)  # not supported by all platforms
            else:
                final_fp = mux_files(audio_path)

        else:
            final_fp = mux_files(audio_path, video_path, subtitle_path, videofps)
        cleanup_files(audio_path, video_path, subtitle_path)
        logging.info(f"Final output file: {final_fp}")

    return 0


def parse_arguments():
    '''set arguments dictionary from supplied arguments'''
    arguments = docopt(__doc__, help=True)
    if arguments['--verbose']:
        log_level = logging.DEBUG
    elif arguments['--quiet']:
        log_level = logging.CRITICAL
    else:
        log_level = logging.INFO

    arguments['log_level'] = log_level

    return arguments


def config_loggers(arguments):
    """ displays the supplied arguments to stdout before switching back to
    the stderr handler

    :param arguments:
    :param log_level:
    :return:
    """

    log_level = arguments['log_level']
    logging.basicConfig(level=log_level)
    logger = logging.getLogger()

    # These lines are needed to create a stdout handler
    # stdout_handler = logging.StreamHandler(stream=sys.stdout)
    # stdout_handler.setLevel(log_level)
    # logger.addHandler(stdout_handler)
    #
    # root_handler = logger.handlers[0]
    # root_handler.setLevel(log_level)
    # logger.removeHandler(root_handler)

    logging.info(f"Supplied args: \n {arguments}")
    # logger.removeHandler(stdout_handler)
    # logger.addHandler(root_handler)


def check_url(arguments):
    ''' parse the url and obtain one if none provided
    Use a provided link or the args provided
    '''
    while len(arguments['URL']) == 0:
        link = input("Provide a youtube link to download: ")
        arguments['URL'].append(link)
        if arguments['URL'][0] == '':
            print("a link must be supplied!")
            del arguments['URL'][0]
    logging.info(f"Final args: {arguments}")

    return arguments


def check_requirements(*args):
    '''ensure executables supplied exist on the file system'''
    logging.debug(f'Requirements: {args}')
    for arg in args:
        status = shutil.which(f'{arg}')
        if status is not None:
            logging.debug(f'Requirement: {arg}  met with {status}')
        else:
            logging.error(f'Requirement: {arg} not met! status: {status}')
            raise Exception(f'Requirement: {arg} not met! status: {status}')


def parse_streams(streams):
    '''
    take yt.streams.all() and print it as a table for viewing
    '''
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


def download_file(download_target, duration=None, start=None):
    '''download stream given a download_target'''
    logging.debug(f"current directory: {Path.cwd()}")
    logging.info(f"Downloading itag: {download_target.itag}")
    logging.info(f"Download url: {download_target.url}")

    fp = Path(download_target.default_filename)
    if start == None:
        start = '0'
    if download_target.type == 'audio':
        fp = ''.join((str(fp.with_suffix('').name),
                      "-audio",
                      fp.suffix
                      ))
    logging.debug(f"Targeting destination: {fp}")
    if duration:
        # download the file with ffmpeg
        # -ss : start point to download in HH:MM:SS.MILLISECONDS format if needed
        # -t : duration to download in seconds
        # -to: end point to download as above format. -t takes precedence
        # NB: -ss before -i sets the -to origin to zero at the cut point
        # -copyts: allows -to to refer to start of clip, no the cut point.

        logging.debug(f"attempting to download {duration} seconds of file")
        cmd = (f'ffmpeg',
               '-ss', f'{start}',
               '-i', f'{download_target.url}',
               '-t', f'{duration}',
               '-c:v', 'copy',
               '-c:a', 'copy',
               f'{fp}')

    else:
        # download the file with aria
        # -c : continue/resume downloads
        # -j : number of parallel downloads for 1 link
        # --optimize-concurrent-downloads=true: optimise speed
        # -x : max connections per server
        # -k : min split size
        # -s, --split=N: Download using N connections

        cmd = ('aria2c',
               '--continue=true',
               '-j5', '-x5',
               '--optimize-concurrent-downloads=true',
               '-k', '1M',
               '--split=5',
               '-o', f'{fp}',
               f'{download_target.url}')

    logging.debug(f"Command to be run: {cmd}")
    subprocess.run(cmd, shell=False, check=True)
    fp = Path(fp)
    logging.info(f"Final {download_target.type} file: {fp}")
    return fp


def download_captions(yt, lang='English', duration=None, start=None):
    i = None
    captions = list(enumerate(yt.captions.all()))
    captions_string = pformat(captions)
    logging.debug(f'captions available: {captions_string}')
    for index, c in captions:
        if lang in str(c):
            i = index
            logging.debug(f'found {lang} captions at index {i}')
            break
    if i is None:
        logging.debug(f'No {lang} Captions found!')
        return None

    subt_base = Path(yt.fmt_streams[0].default_filename).stem
    subt_fp = f'{subt_base}-captions.srt'
    if os.path.exists(subt_fp):
        logging.info(f'File {subt_fp} exists already!! Deleting')
        os.remove(subt_fp)
    with open(subt_fp, 'w', encoding='utf-8') as f:
        logging.debug(f'Writing {subt_fp}')
        lines = yt.captions.captions[i].generate_srt_captions()
        f.write(lines)

    # retime the subtitles
    if start or duration:
        subs = pysrt.open(subt_fp)
        subs.shift(seconds=-int(start))
        part = subs.slice(starts_after={'milliseconds': -1})
        if duration:
            part = part.slice(ends_after=-int(duration))
        part.save(subt_fp)
    return subt_fp


def mux_files(audio_fp, video_fp=None, subt_fp=None, videofps=None):
    '''mux file streams supplied'''
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
        logging.error("no audio or video file path supplied")

    final_fp = "".join((str(final_fp.with_suffix('')),
                        "-output",
                        ".mkv"
                        ))
    audio_fp_text = ('-i', f'{audio_fp}') if audio_fp else ()
    video_fp_text = ('-i', f'{video_fp}') if video_fp else ()
    subt_fp = () if subt_fp is None else ('-i', f'{subt_fp}')
    subt_text = ('-c:s', 'srt') if subt_fp else ()
    videofps_text = ('-r', f'{videofps}') if videofps else ()
    if Path(final_fp).is_file():
        logging.error(f"{final_fp} already exists! Will overwrite...")

    cmd = ('ffmpeg',
           '-y',
           *audio_fp_text,
           *video_fp_text,
           *subt_fp,
           *videofps_text,
           '-c:a', 'copy',
           '-c:v', 'copy',
           *subt_text,
           f'{final_fp}')
    logging.debug(f"Command to be run: {cmd}")
    subprocess.run(cmd, shell=False, check=True)
    logging.info(f"Final muxed file: {final_fp}")

    return final_fp


def cleanup_files(audio_path, subtitle_path, video_path):
    '''cleanup file paths supplied'''
    logging.info("CLEANUP:")
    for k, v in {'audio'    : audio_path,
                 'video'    : video_path,
                 'subtitles': subtitle_path}.items():
        if v:
            logging.info(f"CLEANUP: deleting {k} file: {v}")
            # check for errors
            errors = os.remove(v)
            if not errors:
                logging.info("Success!")
            else:
                logging.error(f"Error code detected: {errors}")
        else:
            logging.debug(f'CLEANUP: no {k} file detected')


def make_mp3(audio_path):
    '''convert from a webm file to an mp3'''
    logging.debug(f"current directory: {Path.cwd()}")
    fp = audio_path.with_suffix('.mp3')
    logging.debug(f"Targeting destination: {fp}")

    # convert the file
    # -i : input file name
    # -c:a libmp3lame  : create mp3 file using lame codec
    # -q:a 0   : highest variable audio quality
    # -n : exit immediately if file exists
    # -y : overwrite output files without asking
    if Path(fp).is_file():
        logging.error(f"{fp} already exists! Will overwrite...")
    cmd = ('ffmpeg',
           '-y',
           '-i', f'{audio_path}',
           '-c:a', 'libmp3lame',
           '-q:a', '0',
           f'{fp}')
    logging.debug(f"Command to be run: {cmd}")
    subprocess.run(cmd, shell=False, check=True)
    fp = Path(fp)
    return fp


def make_ogg(audio_path):
    '''convert from a webm file to an ogg'''
    logging.debug(f"current directory: {Path.cwd()}")
    fp = audio_path.with_suffix('.ogg')
    logging.debug(f"Targeting destination: {fp}")

    # convert the webm -> ogg
    # -c:a copy : use the same audio codec
    # -n : exit immediately if file exists
    # -y : overwrite output files without asking
    if Path(fp).is_file():
        logging.error(f"{fp} already exists! Will overwrite...")
    cmd = ('ffmpeg',
           '-y',
           '-i', f'{audio_path}',
           '-c:a', 'libopus',
           '-b:a', '160k',
           f'{fp}')

    logging.debug(f"Command to be run: {cmd}")
    subprocess.run(cmd, shell=False, check=True)
    fp = Path(fp)
    return fp


def make_aac(audio_path):
    '''convert from a file to an aac'''
    logging.debug(f"current directory: {Path.cwd()}")
    fp = audio_path.with_suffix('.aac')
    logging.debug(f"Targeting destination: {fp}")

    # convert the file
    # -i : input file name
    # -c:a aac  : create aac file
    # -q:a 0   : highest variable audio quality
    # -profile:a aac_ltp : Long term prediction profile, is enabled by and will enable
    # the aac_ltp option. Introduced in MPEG4.
    # -n : exit immediately if file exists
    # -y : overwrite output files without asking
    if Path(fp).is_file():
        logging.error(f"{fp} already exists! Will overwrite...")
    cmd = ('ffmpeg',
           '-y',
           '-i', f'{audio_path}',
           '-c:a', 'aac',
           '-q:a', '0',
           '-profile:a', 'aac_main'
                         f'{fp}')
    logging.debug(f"Command to be run: {cmd}")
    subprocess.run(cmd, shell=False, check=True)
    fp = Path(fp)
    return fp


if __name__ == '__main__':
    downloader()
