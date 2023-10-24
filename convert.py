# Convert flac CD images to iTunes compatible mp3 files
#
# Given an input folder containing folders of .flac and .flac.cue CD images,
# split into them in single tracks and output folders of mp3 files into the output folder.

import os
import sys
import concurrent.futures
import shlex
from deflacue import deflacue

input = sys.argv[1]
output = sys.argv[2]
print(f"Reading flac folders from {input} and writing mp3s to {output}")


def sanitize(val: str) -> str:
    return val.replace('/', '')


def process_folder(folder: str):
    tracks_processed = 0

    flac_file = None
    cue_file = None
    folder_files = os.listdir(os.path.join(input, folder))
    for file in folder_files:
        if file.endswith(".flac"):
            flac_file = file
            # With matching cue file?
            expected_cue_file = flac_file + ".cue"
            if expected_cue_file in folder_files:
                cue_file = expected_cue_file

    if (flac_file is not None) & (cue_file is not None):
        flac_path = os.path.join(input, folder, flac_file)

        # Parse the cue file
        parser = deflacue.CueParser.from_file(os.path.join(input, folder, cue_file))
        cue_data = parser.run
        cue = parser.run()
        cd_info = cue.meta.data
        tracks = cue.tracks
        cd_title = cd_info['ALBUM']
        cd_performer = cd_info['PERFORMER']
        print(f"{cd_performer} / {cd_title} : {flac_file}")

        output_folder = os.path.join(output, folder)
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)

        len_tracks_count = len(str(len(tracks)))
        for track in tracks:
            tracks_processed += 1
            num = str(track.num).rjust(len_tracks_count, '0')
            title = track.data['TITLE']
            # TODO if 'PERFORMER': 'Various Artists' then split title on / to get better artist and title

            track_filename = str(num) + "-" + sanitize(title) + ".mp3"
            out_filepath = os.path.join(output_folder, track_filename)
            track_exists = os.path.isfile(out_filepath)
            if not track_exists:
                print(f"Rendering mp3 file: {out_filepath}")

                trim = "-af atrim=start_sample=" + str(track.start)
                if track.end > 0:
                    trim += ":end_sample=" + str(track.end)
                trim += ",asetpts=N/SR/TB"

                meta = "-metadata title=" + shlex.quote(title) + " -metadata track=" + str(track.num) + "/" + str(
                    len(tracks)) + " " + "-map_chapters -1"

                cmd = "ffmpeg -loglevel warning -i " + shlex.quote(
                    flac_path) + " " + trim + " " + meta + " " + "-c:a mp3 -b:a 192k" + " " + shlex.quote(out_filepath)
                print(cmd)
                result = os.system(cmd)
                if result != 0:
                    exit(result)

        return tracks_processed


sub_folders = [name for name in os.listdir(input) if os.path.isdir(os.path.join(input, name))]

tracks_processed = 0
for folder in sub_folders:
    # Foreach folder look for a flac file
    tracks_processed += process_folder(folder)

print(f"Finished. Processed {tracks_processed} tracks.")

# Execute foreach folder in parallel
# executor = concurrent.futures.ProcessPoolExecutor(10)
# futures = [executor.submit(process_folder, folder) for folder in os.listdir(input) if os.path.isdir(os.path.join(input, folder))]
##futures = [executor.submit(process_folder, folder) for folder in sub_folders]
# concurrent.futures.wait(futures)
