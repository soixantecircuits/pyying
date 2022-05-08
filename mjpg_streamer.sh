#!/usr/bin/env sh
: <<COMMENTBLOCK
author			:Valeriu Stinca
email				:ts@strategic.zone
date				:2022-04-25
version			:0.1
notes				:
===============================
COMMENTBLOCK
/usr/local/bin/mjpg_streamer -i "/usr/local/lib/input_file.so -d 0 -r -f /tmp/stream" -o "/usr/local/lib/output_http.so -w /usr/local/share/www/ -p 36700"