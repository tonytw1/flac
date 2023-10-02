input = "/mnt/cds"
output = "/mnt/split"

import os
from deflacue import deflacue

sub_folders = [name for name in os.listdir(input) if os.path.isdir(os.path.join(input, name))]

for folder in sub_folders:
	# Foreach folder look for a flac file
	flac_file = None
	cue_file = None
	folder_files = os.listdir(os.path.join(input, folder))
	for file in folder_files:
		if file.endswith(".flac"):
			flac_file = file
			# With matching cue file?
			expected_cue_file = flac_file + ".cue"
			if (expected_cue_file in folder_files):
				cue_file = expected_cue_file

	if (flac_file is not None) & (cue_file is not None):
		print (folder + ": " + flac_file + " / " + cue_file)
		# Split flac into tracks with metadata
		splitter = deflacue.Deflacue(source_path = os.path.join(input, folder), dest_path=output)
		splitter.do()

