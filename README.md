Simple application that turn a camera into an IP camera, and takes pictures with OSC command.

Install instructions to be updated soon.

Install pyying
--------------
```
sudo apt-get install python-pygame python-pip gphoto2 libgphoto2-2-dev libgphoto2-port0
sudo pip install pyOSC

cd ~/sources
mkdir python
mkdir python/soixante
cd python/soixante
git clone git@github.com:soixantecircuits/pyying.git
cd pyying
python pyying.py
```

Install mjpg-streamer
---------------------

With mjpg-streamer, you can convert the jpeg stream from pyying to a MJPEG stream, that can be read in a browser

```
sudo apt-get install libjpeg62-dev imagemagick subversion
svn co https://svn.code.sf.net/p/mjpg-streamer/code/mjpg-streamer
cd mjpg-streamer
make
sudo make install
```

Run
---

Run pyying
```
$ cd ~/sources/python/soixante/pyying
$ python pyying.py
```

In another window, run mjpg-streamer
```
$ mjpg_streamer -i "/usr/local/lib/input_file.so -r -f /tmp/stream" -o     "/usr/local/lib/output_http.so -w /usr/local/www -p 8080"
```

See it in browser

http://127.0.0.1:8080/?action=stream
