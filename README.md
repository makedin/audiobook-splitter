# audiobook-splitter

This scrtipt calls [mpv](https://mpv.io/) to split an audio file into multiple shorter files. It also supports speeding up (or slowing down) the audio in the resulting files. It depends on Python 3.7+, mpv and, optionally, mediainfo (for determining the length of the input file).

```
python split.py --help
usage: split.py [-h] [-s HH:MM:SS] [-e HH:MM:SS] [--speedup <float>]
                [-d <float>] [-o OUTPUTDIR] [-f <filetype>] [-p PREFIX]
                [-n <integer>] [-t <integer>] [--dry-run]
                FILE

Split up an audio file into multiple shorter files.

positional arguments:
  FILE

optional arguments:
  -h, --help            show this help message and exit
  -s HH:MM:SS, --start HH:MM:SS
                        the starting position of the first part (defaults to
                        00:00:00)
  -e HH:MM:SS, --end HH:MM:SS
                        the ending position of the last part (defaults to the
                        end of the track)
  --speedup <float>     speed up factor (defaults to 1.0)
  -d <float>, --duration <float>
                        length of an individual part in minutes (defaults to
                        20)
  -o OUTPUTDIR, --outputdir OUTPUTDIR
                        the directory to output the newly split parts
                        (defaults to the working directory)
  -f <filetype>, --format <filetype>
                        the audio format to use for output (defaults to ogg)
  -p PREFIX, --prefix PREFIX
                        the prefix part of new files' names (defaults to the
                        original file's name)
  -n <integer>, --numbering-start <integer>
                        the position to start the new files'numbering from
                        (defaults to 1)
  -t <integer>, --threads <integer>
                        the number of worker threads to spawn (defaults to 2)
  --dry-run             show the new files that would be created if run
                        without this flag
 ```
