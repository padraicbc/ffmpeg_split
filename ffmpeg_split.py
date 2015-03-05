import re
import math
from optparse import OptionParser

length_regexp = 'Duration: (\d{2}):(\d{2}):(\d{2})\.\d+,'
re_length = re.compile(length_regexp)

from subprocess import check_call, PIPE, Popen
import shlex

def main():
    filename, split_length = parse_options()
    if split_length <= 0:
        print("Split length can't be 0")
        raise SystemExit

    p1 = Popen(["ffmpeg", "-i", filename], stdout=PIPE, stderr=PIPE, universal_newlines=True)
    # get p1.stderr as input
    output = Popen(["grep", 'Duration'], stdin=p1.stderr, stdout=PIPE, universal_newlines=True)
    p1.stdout.close()
    matches = re_length.search(output.stdout.read())
    if matches:
        video_length = int(matches.group(1)) * 3600 + \
                       int(matches.group(2)) * 60 + \
                       int(matches.group(3))
        print("Video length in seconds: {}".format(video_length))
    else:
        print("Can't determine video length.")
        raise SystemExit

    split_count = math.ceil(video_length / split_length)

    if split_count == 1:
        print("Video length is less than the target split length.")
        raise SystemExit

    for n in range(split_count):
        split_start = split_length * n
        pth, ext = filename.rsplit(".", 1)
        cmd = "ffmpeg -i {} -vcodec copy  -strict -2 -ss {} -t {} {}-{}.{}".\
            format(filename, split_start, split_length, pth, n, ext)
        print("About to run: {}".format(cmd))
        check_call(shlex.split(cmd), universal_newlines=True)


def parse_options():
    parser = OptionParser()

    parser.add_option("-f", "--file",
                      dest="filename",
                      help="file to split, for example sample.avi",
                      type="string",
                      action="store"
    )
    parser.add_option("-s", "--split-size",
                      dest="split_size",
                      help="split or chunk size in seconds, for example 10",
                      type="int",
                      action="store"
    )
    (options, args) = parser.parse_args()

    if options.filename and options.split_size:

        return options.filename, options.split_size

    else:
        parser.print_help()
        raise SystemExit

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
