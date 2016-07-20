from __future__ import print_function
import os
import sys
import glob
import shutil
import argparse
import subprocess


map(os.remove, glob.glob("box*"))
map(os.remove, glob.glob("temp*"))

# cmd_loss = "bmdcapture -C 0 -m 10 -A 2 -V 3 -F nut -f pipe:1 2>/dev/null | ffmpeg -i - -s 1920x1080 -vcodec libx264 -crf 0 -preset ultrafast temp.mkv > /dev/null 2>/dev/null &"
cmd_no_hls = "bmdcapture -C 0 -m 10 -A 2 -V 3 -F nut -f pipe:1 2>/dev/null | ffmpeg -i - -c:a aac -strict experimental -ac 2 -b:a 64k -b:v 8192k -ar 44100 -vcodec libx264 -f hls -hls_time 9 -hls_list_size 10 -s 1920x1080 -preset ultrafast box.m3u8"
cmd_with_hls = """bmdcapture -C 0 -m 10 -A 2 -V 3 -F nut -f pipe:1 2>/dev/null | ffmpeg -i - \
-vcodec libx264 -ac 2 -strict experimental -crf 40 \
-profile:v baseline -maxrate 800k \
-ar 44100 -c:a aac -s 1280x720 -preset ultrafast \
-pix_fmt yuv420p -flags -global_header -b:a 64k -b:v 900k \
-hls_time 10 -hls_list_size 3 -hls_wrap 4 -hls_flags delete_segments \
-start_number 1 hls/box1.m3u8 \
-vcodec libx264 -ac 2 -strict experimental -crf 30 \
-profile:v baseline -maxrate 2000k \
-ar 44100 -c:a aac -s 1920x1080 -preset ultrafast \
-pix_fmt yuv420p -flags -global_header -b:a 64k -b:v 4096k \
-hls_time 10 -hls_list_size 3 -hls_wrap 4 -hls_flags delete_segments \
-start_number 1 hls/box2.m3u8 \
-vcodec libx264 -ac 2 -strict experimental -crf 18 \
-profile:v baseline -maxrate 8000k \
-ar 44100 -c:a aac -s 1920x1080 -preset ultrafast \
-pix_fmt yuv420p -flags -global_header -b:a 64k -b:v 8192k \
-hls_time 10 -hls_list_size 3 -hls_wrap 4 -hls_flags delete_segments \
-start_number 1 hls/box3.m3u8
"""
box = """#EXTM3U
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=800000
hls/box1.m3u8
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=4000000
hls/box2.m3u8
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=8000000
hls/box3.m3u8
"""


def retry(nb_retry):
    def dec_func(func):
        def wrapper(*args):
            for r in range(1, nb_retry + 1):
                print('run ffmpeg x ' + str(r))
                func(*args)
        return wrapper
    return dec_func


@retry(3)
def loop_ffmpeg(with_hls):
    cmd = cmd_with_hls if with_hls else cmd_no_hls
    if with_hls:
        if os.path.exists("hls"):
            shutil.rmtree("hls")
        if os.path.exists("box.m3u8"):
            os.remove("box.m3u8")
        os.mkdir("hls")
        with open('box.m3u8', mode='w') as file:
            file.write(box)
    try:
        encode_output = subprocess.Popen(cmd, shell=True)
        encode_output.communicate()
    except KeyboardInterrupt:
        encode_output.kill()
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description='Transcoding for blackmagic\'input'
    )
    parser.add_argument(
        '--hls', action='store_true',
        dest='hls',
        help='set transcoding with hls'
    )
    args = parser.parse_args()
    loop_ffmpeg(args.hls)

if __name__ == '__main__':
    main()
