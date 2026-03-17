#!/bin/bash

# This script  is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This script  is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with This script ; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 
# USA.

# # # #
# Encoding videos for YouTube with FFMpeg
# by: Jernej Virag
# #######################################
# URL: https://virag.si/2015/06/encoding-videos-for-youtube-with-ffmpeg/
# #######################################
# ffmpeg -i <input file> -codec:v libx264 -crf 21 -bf 2 -flags +cgop -pix_fmt yuv420p -codec:a aac -strict -2 -b:a 384k -r:a 48000 -movflags faststart <output_name>.mp4
# ABOVE LINE IS MODIFIED TO SUITE THIS BATCH ENCODING SCRIPT AS UNDER: JUST FOR m4a encoding without video.
# ffmpeg -i "$INPUT_FILE" -codec:v libx264 -crf 21 -bf 2 -r "$frame_rate" -s "$resolution" -aspect "$aspect" -flags +cgop -pix_fmt yuv420p -codec:a aac -b:a 256k -r:a 48000 -ac "$channels" -movflags faststart "$OUTPUT_FILE"
# # # #

# ################################################################################################################################
# BATCH CONVERTER 
#
# This script targets .avi as an input file(s) and converts into .mp4
# You can change input target from .avi to any like .mkv at line# 56
# by replacing .avi to .mkv i.e INPUT_EXT=.avi to INPUT_EXT=.mkv
# ################################################################################################################################
# Checking if ffmpeg is installed.
ffmpeg=`which ffmpeg`
ffprobe=`which ffprobe`
EXITCODE=101

if (test ! -n "$ffprobe"); 
then
clear
echo
echo "********************************" 
echo "* You have to install ffprobe. *"
echo "********************************"
echo
exit "$EXITCODE"
fi

if (test -n "$ffmpeg"); 
then 

# Specify input and output file extensions
INPUT_EXT=.avi  # extension .avi can be replace with any valid video extension like .mkv 
OUTPUT_EXT=.mp4

# Specify input and output directories.
# "/path/to/some/directory"
# Here input and poutput directory is `pwd` or "$(PWD)" -> Current Directory.

INPUT_DIR=`pwd` # "$(PWD)" can be replaced with "/path/to/input/directory" 
OUTPUT_DIR=`pwd` # "$(PWD)" can be replaced with "/path/to/output/directory"

# ################################################
# NewBies, Do NOT modify anything below.
# If you want, back-up this script and go-ahed.
# ################################################

# Counting total files for encoding. 
# If count is zero then nothing to do!

COUNT=`ls -l *"$INPUT_EXT" | grep ^- | wc -l`
echo
echo "Total $COUNT file(s) to encode ..."
echo

if [ "$COUNT" -gt 0 ]; 
then

for f in *$INPUT_EXT; do
  
  INPUT_FILE="$INPUT_DIR/$f"
  OUTPUT_FILE="$OUTPUT_DIR/${f%$INPUT_EXT}$OUTPUT_EXT"
  ## USING ffprobe TO GET MEDIA INFORMATION
  resolution=`ffprobe -v error -select_streams v:0 -show_entries stream=height,width -of csv=s=x:p=0 "$INPUT_FILE"`
  frame_rate=`ffprobe -v error -select_streams v:0 -show_entries stream=avg_frame_rate -of default=noprint_wrappers=1:nokey=1 "$INPUT_FILE"`
  aspect=`ffprobe -v error -select_streams v:0 -show_entries stream=display_aspect_ratio -of default=noprint_wrappers=1:nokey=1 "$INPUT_FILE"`
  channels=`ffprobe -v error -select_streams v:1 -show_entries format=nb_streams -of default=noprint_wrappers=1:nokey=1 -sexagesimal "$INPUT_FILE"`
  ## USING ffmpeg to COVERT  
  echo
  echo "Now encoding file: " $INPUT_FILE
  ffmpeg -i "$INPUT_FILE" -codec:v libx264 -crf 21 -bf 2 -r "$frame_rate" -s "$resolution" -aspect "$aspect" -flags +cgop -pix_fmt yuv420p -codec:a aac -b:a 256k -r:a 48000 -ac "$channels" -movflags faststart "$OUTPUT_FILE"
  wait
  
done

else
echo "File with "$INPUT_EXT" extension does not exist."

fi

echo
echo "Total "$COUNT" file(s) has been encoded."
echo

else
clear
echo
echo "********************************" 
echo "* You have to install ffmpeg. *"
echo "********************************"
echo
fi

exit 0
