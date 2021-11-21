"""
#!/bin/bash
# https://stackoverflow.com/questions/7427262/how-to-read-a-file-into-a-variable-in-shell
VIDEO_PATH=$1
SEGMENTS=$(<$2)

# https://superuser.com/questions/692714/how-to-split-videos-with-ffmpeg-and-segment-times-option
DIR="$VIDEO_PATH output"
mkdir "$DIR"
ffmpeg -i "$VIDEO_PATH" -f segment -segment_times $SEGMENTS \
-c:v copy -map 0 -c:a copy \
-reset_timestamps 1 "$DIR/$1-word%d.mov"
# ffmpeg -i "$VIDEO_PATH" -f segment -segment_times $SEGMENTS -c copy \
# -vcodec vp9 \
# -acodec libvorbis -map 0 \
#-reset_timestamps 1 "$DIR/$1-word%d.webm"

# References:
# Time unit syntax: https://trac.ffmpeg.org/wiki/Seeking#Timeunitsyntax
# Reset timestamps to avoid all videos black but the
# first: https://trac.ffmpeg.org/ticket/142://trac.ffmpeg.org/ticket/1425
"""

# Get the CSV file with times and words
# Verify CSV file is in proper format
# Get the video file
# Verify timestamps and video length match up
# Create tmpdir
# run FFMPEG script on the file, doing output to the tmpdir
# Return a file path to a zip file


