#!/bin/bash

# This script runs VeraPDF and JHOVE on all PDF files in a directory, and
# reports output to individual files. In addition, it runs 3
# Python scripts that extract output on Actions and Annotations. The
# output is subsequently written to 3 Markdown formatted tables.

# Locations of VeraPDF and JHOVE
veraPDF=~/verapdf/verapdf
jhove=~/jhove/jhove

# Installation directory
instDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# In- and output dirs
dirIn="$1"
dirOut="$2"

# Check arguments
if [ "$#" -ne 2 ] ; then
  echo "Usage: analysis-vera-jhove dirIn dirOut" >&2
  exit 1
fi

if ! [ -d $dirIn ] ; then
  echo "Input directory does not exist" >&2
  exit 1
fi

# Create output directory if it doesn't exist already
if ! [ -d $dirOut ] ; then
    mkdir $dirOut
fi

# Output table
tabActionsAnnots="$dirOut"/actions-annots.md

# Write headers to output table
echo "|File|Actions (VeraPDF)|Annotations (VeraPDF)|Annotations (JHOVE)|" > "$tabActionsAnnots"
echo "|:--|:--|:--|:--|" >> "$tabActionsAnnots"

# **************
# MAIN PROCESSING LOOP
# **************

counter=0

while IFS= read -d $'\0' file ; do
    # Base name (strip away path)
    fileNameIn=$(basename "$file")
    baseName="${fileNameIn%.*}"
    
    # Generate output file names
    outVera="$dirOut""/""$baseName"-vera.xml
    outJhove="$dirOut""/""$baseName"-jhove.xml

    # Run VeraPDF and JHOVE
    "$veraPDF" --off --extract "$file" > "$outVera"
    "$jhove" -m PDF-hul -h XML -i "$file" -o "$outJhove"

    # Run analysis scripts that extract actions and annotations from
    # VeraPDF and Jhove output
    actionsVera=$(python3 "$instDir"/vera-actions.py "$outVera" "<br>")
    annotsVera=$(python3 "$instDir"/vera-annots.py "$outVera" "<br>")
    annotsJhove=$(python3 "$instDir"/jhove-annots.py "$outJhove" "<br>")

    # Add output of scripts to tables
    echo "|""$fileNameIn""|""$actionsVera""|""$annotsVera""|""$annotsJhove""|" >> "$tabActionsAnnots"

done < <(find $dirIn -type f -regex '.*\.\(pdf\|PDF\)' -print0)
