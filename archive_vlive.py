"""
Command-line interface script to download ALL non-autotranslation subtitles from VLIVE videos
Lets the user also download the video with -v
Add -d to only download subtitles for languages that have multiple official and/or multiple fan subs
"""

import argparse
import os
import re
import requests

from yt_dlp import YoutubeDL

REGEX_VLIVE_SUB = re.compile(r'(?P<lang>[a-z]{2}(_[A-Z]{2})?)(_(?P<type>cp|fan))?\.vtt$')


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("urls", type=str, nargs='+', help="Space-separated list of VLIVE channel/video URLs")
    # parser.add_argument("-p", "--path", type=str, help="Output path")
    parser.add_argument("-v", "--video", action="store_true", help="Also download video")
    parser.add_argument("-d", "--dupes-only", action="store_true",
                        help="Only download subtitles where language-type occur multiple times")
    return parser.parse_args()


def download_subs(video_dict, filename, dupes_only=False):
    """Save all subtitle files for a video named <filename> in unique files"""
    for language, subtitles in video_dict['subtitles'].items():
        type_dict = {'cp': [], 'fan': []}
        for subtitle in subtitles:
            if subtitle['ext'] == 'vtt':
                match = REGEX_VLIVE_SUB.search(subtitle['url'])
                if not match:
                    print(f'[archive] WARNING: skipping subtitle because REGEX did not match {subtitle["url"]}')
                    continue

                # Keep track of type occurrences
                type_dict[match['type'] or 'cp'].append(subtitle['url'])

        # Download and write subtitle content to <filename>_<language code>_<type>_<occurrence>.vtt
        for _type, urls in type_dict.items():
            if (dupes_only and len(urls) > 1) or not dupes_only:
                for i, url in enumerate(urls):
                    filename_sub = f'{os.path.splitext(filename)[0]}.{language}_{_type}_{i+1}.vtt'
                    r = requests.get(url, allow_redirects=True)
                    with open(filename_sub, 'wb') as f:
                        f.write(r.content)


def main():
    args = get_args()

    ydl_opts = {
        'noplaylist': True,
        'outtmpl': '%(upload_date>%y%m%d)s %(title)s [%(id)s].%(ext)s'
    }

    with YoutubeDL(ydl_opts) as ydl:
        for url in args.urls:
            info = ydl.extract_info(url, download=args.video)
            info_dict = ydl.sanitize_info(info)
            if "entries" in info_dict:  # channel/playlist
                videos = info_dict['entries']
                for video in videos:
                    filename = ydl.prepare_filename(video)
                    download_subs(video, filename, dupes_only=args.dupes_only)
            else:  # single video
                filename = ydl.prepare_filename(info)
                download_subs(info_dict, filename, dupes_only=args.dupes_only)


if __name__ == '__main__':
    main()
