#!/usr/bin/python

from subprocess import Popen, PIPE
from time import gmtime, strftime
from queue import Queue
from threading import Thread
import argparse
from sys import stderr, exit
from os import path, mkdir

parser = argparse.ArgumentParser(description="Split up an audio file into "
        "multiple shorter files.")

parser.add_argument("filename", metavar="FILE")
parser.add_argument("-s", "--start", metavar="HH:MM:SS",
        help="the starting position of the first part (defaults to 00:00:00)")
parser.add_argument("-e", "--end", metavar="HH:MM:SS",
        help="the ending position of the last part (defaults to "
        "the end of the track)")
parser.add_argument("--speedup", type=float, default=1.0, metavar="<float>",
        help="speed up factor (defaults to 1.0)")
parser.add_argument("-d", "--duration", type=float, default=20.0,
        metavar="<float>",
        help="length of an individual part in minutes (defaults to 20)")
parser.add_argument("-o", "--outputdir", help="the directory to output "
        "the newly split parts (defaults to the working directory)")
parser.add_argument("-f", "--format", metavar="<filetype>", default="ogg",
        help="the audio format to use for output (defaults to ogg)")
parser.add_argument("-p", "--prefix", help="the prefix part of new files' "
        "names (defaults to the original file's name)")
parser.add_argument("-n", "--numbering-start", type=int, default=1,
        metavar="<integer>", help="the position to start the new files'"
        "numbering from (defaults to 1)")
parser.add_argument("-t", "--threads", type=int, default=2, metavar="<integer>",
        help="the number of worker threads to spawn (defaults to 2)")
parser.add_argument("--dry-run", action="store_const",
        const=True, default=False, help="show the new files that would be "
        "created if run without this flag")




args = parser.parse_args()


def get_file_length(filename):
    fileend = False
    try:
        info = Popen(["mediainfo", "--Output=Audio;%Duration%", filename],
                stdout=PIPE)
        if info.wait() == 0:
            lenstring = info.stdout.read().strip()
            if lenstring.isdigit():
                fileend = int(lenstring)/1000

    except FileNotFoundError:
        error_print("mediainfo not found", "warning")
        if args.end is None:
            error_print("end time must be supplied", "error")

    return fileend

def format_time(sec):
    return strftime("%H:%M:%S", gmtime(sec))

def parse_time(time):
    hhmmss = time.strip().split(":")
    if len(hhmmss) != 3:
        error_print(f'badly formatted time "{time}"', "error");
        return False
    i = 0
    for place in hhmmss:
        if not place.isdigit():
            return False
        hhmmss[i] = int(place)
        i += 1

    if hhmmss[1] > 59 or hhmmss[2] > 59:
        return False
    return hhmmss[0] * 3600 + hhmmss[1] * 60 + hhmmss[2]


def split_part(filename, start, end, speedup, outfile):
    return Popen(["mpv", "--af=scaletempo", "--no-terminal",
        f"--start={format_time(start)}", f"--end={format_time(end)}",
        f"--speed={str(speedup * 1.0)}",
        filename, f"-o={outfile}"])

def split_dispatcher():
    while True:
        params = work_queue.get()
        p = split_part(params[0], params[1], params[2], params[3], params[4])
        if p.wait() != 0:
            print(f'Error splitting part starting at {params[1]} \
                    and ending at {params[2]} into {params[4]}')
        work_queue.task_done()

def error_print(msg, level):
    print(f"{level}: {msg}", file=stderr)


if not path.isfile(args.filename):
    error_print(f'file not found "{args.filename}"', "error")
    exit(1)

if not args.start is None:
    start = parse_time(args.start)
    if not start:
        error_print('invalid start time', 'error');
        exit(1)
else:
    start = 0

if not args.end is None:
    end = parse_time(args.end)
    if not end:
        error_print('invalid end time', 'error');
        exit(1)
else:
    end = get_file_length(args.filename)

if args.speedup <= 0:
    error_print("speedup factor must be greater than zero", "error")
    exit(1)

if args.threads < 1:
    error_print("the number of worker threads must be at least 1", "error")
    exit(1)

if args.prefix is None:
    prefix = f"{path.split(path.splitext(args.filename)[0])[1]}-"
else:
    prefix = args.prefix
    if len(prefix) > 0:
        prefix = f"{prefix}-"

if not args.outputdir is None:
    outputdir = args.outputdir + "/"
    if not path.isdir(outputdir):
        mkdir(outputdir)
else:
    outputdir = ""


work_queue = Queue()


duration = args.duration * 60
for i in range(args.threads):
    thread = Thread(target=split_dispatcher)
    thread.daemon = True
    thread.start()

part = args.numbering_start
while (start < end):
    if start + duration < end:
        partend = start + duration
    else:
        partend = end

    outfilename = path.join(outputdir, f"{prefix}{str(part)}.{args.format}")
    if args.dry_run:
        print(f"{outfilename} [{format_time(start)}-{format_time(partend)}]")
    else:
        work_queue.put((args.filename, start, partend, args.speedup,
            outfilename));

    start += duration
    part += 1

work_queue.join()
