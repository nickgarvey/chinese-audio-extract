#!/bin/bash

for x in *mp3; do
    nn=$(echo $x | sed -e 's/mp3$/flac/')
    if [ ! -s "$nn" ]; then
        sem -j4 -- ffmpeg -i $(printf '%q' "$x") $(printf '%q' "$nn")
    fi
done

sem --wait
echo done!
