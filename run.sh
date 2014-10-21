#/bin/bash
# This script runs mjpg_streamer and pyying and allows you to kill them properly

DIR=$(dirname $0);

# echo "${BBlu} Launching mjpg_streamer ... ${RCol}"
trap close INT TERM QUIT
close(){
  echo "close"
  kill -15 $PYYING
  kill -15 $MJPG_STREAM
  exit
}

#echo "\033[1m" 'Launching mjpg_streamer ...' "\033[0m"

#mkdir -p /tmp/stream
#mjpg_streamer -i "/usr/local/lib/input_file.so -r -f /tmp/stream" -o "/usr/local/lib/output_http.so -w /usr/local/www -p 8080" &
#MJPG_STREAM="$!"

echo "\033[1m" 'Launching pyying ...' "\033[0m"

python $DIR/pyying.py --nowindow &
PYYING="$!"
echo $PYYING


wait
