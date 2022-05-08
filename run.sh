#/bin/bash
# This script runs pyying and allows you to kill them properly

DIR=$(dirname $0);

trap close INT TERM QUIT
close(){
  echo "close"
  kill -15 $PYYING
  #kill -15 $MJPG_STREAM
  exit
}

#echo "\033[1m" 'Launching mjpg_streamer ...' "\033[0m"

#mkdir -p /tmp/stream
#mjpg_streamer -i "/usr/local/lib/input_file.so -r -f /tmp/stream" -o "/usr/local/lib/output_http.so -w /usr/local/www -p 8080" &
#MJPG_STREAMER_CMD="$!"
#echo $MJPG_STREAM_CMD

echo "\033[1m" 'Launching pyying ...' "\033[0m"

python $DIR/pyying.py --nowindow true &
PYYING_CMD="$!"
echo $PYYING_CMD

wait
