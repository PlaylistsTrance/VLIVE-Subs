import argparse
from datetime import datetime
import os
import re
import requests
import time
import unicodedata

import vlivepy.board
import vlivepy.channel
import vlivepy.exception
import vlivepy.model


MAX_TRIES = 10
RE_WINDOWS = re.compile(r"[<>:\"/\\|?*]")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="File with list of channel boards")
    return parser.parse_args()


def slugify(value):
    return RE_WINDOWS.sub("", value)


def old_code():
    grouped_boards = vlivepy.channel.getGroupedBoards(match['channel'])
    star_board = None
    for board_group in grouped_boards:
        if board_group['groupTitle'] == "Official":
            for board in board_group['boards']:
                if board['boardType'] == "STAR":
                    star_board = board
                    break
        if star_board:
            break
    else:
        print("No STAR board found.")
        return
    star_board['boardId']


def post_url(video_id):
    return f"https://vlive.tv/post/{video_id}"


def main():
    args = get_args()
    url_rule = re.compile(r'(?P<channel>[A-Z0-9]+)/board/(?P<board>\d+)')
    dupes_only = False
    with open(args.file, 'r') as f:
        urls = f.read().splitlines()
    for url in urls:
        match = url_rule.search(url)
        if not match:
            print(f"\"{url}\" did not match a channel board URL")
            return

        channel = vlivepy.model.Channel(match['channel'])
        channel_name = channel.channel_name

        print(f"Downloading subs for channel {channel_name}...")
        subs_found = 0
        for board_post in vlivepy.board.getBoardPostsIter(match['channel'], match['board']):
            if board_post.has_official_video:
                post = board_post.to_object()
                video = post.official_video()
                for _ in range(MAX_TRIES):
                    try:
                        video_info = video.getVodPlayInfo()
                        break
                    except vlivepy.exception.APINetworkError:
                        time.sleep(1)
                else:
                    print(f"ERROR: Was not able to download subtitles for {post_url(post.post_id)}")
                    continue
                upload_date = datetime.utcfromtimestamp(video.created_at).strftime('%y%m%d')
                filename = f"{slugify(channel_name)}/{upload_date} {slugify(video.title)} [{post.post_id}]"
                captions = video_info.get("captions", dict()).get("list", list())
                print(f"{post_url(post.post_id)} has {len(captions)} caption{'s'*int((len(captions) != 1))}.")
                subs_found += len(captions)
                if not os.path.exists(os.path.dirname(filename)) and captions:
                    os.mkdir(os.path.dirname(filename))
                type_dict = {}
                for caption in captions:
                    locale_type = caption['locale'], caption['type']
                    if locale_type in type_dict:
                        type_dict[locale_type].append(caption)
                    else:
                        type_dict[locale_type] = [caption]
                for locale_type, captions in type_dict.items():
                    if (dupes_only and len(captions) > 1) or not dupes_only:
                        for i, caption in enumerate(captions):
                            caption_num = f"_{i+1}" if len(captions) > 1 else ""
                            filename_sub = f"{filename}.{locale_type[0]}_{locale_type[1]}{caption_num}.vtt"
                            r = requests.get(caption['source'], allow_redirects=True)
                            with open(filename_sub, 'wb') as f:
                                f.write(r.content)
        print(f"{subs_found} captions downloaded from {channel_name}!")


if __name__ == '__main__':
    main()
