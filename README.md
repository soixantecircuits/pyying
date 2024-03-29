Simple application that turn a camera into an IP camera, and takes pictures with OSC command.

Install instructions to be updated soon.

Install pyying
--------------
```
sudo apt-get install python-pygame python-pip gphoto2 libgphoto2-2-dev libgphoto2-port0
sudo pip install -r requirements.txt

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

You can run pyying and mjpeg_streamer at the same time by typing:
```
$ sh run.sh
```

Or you can separately run pyying
```
$ cd ~/sources/python/soixante/pyying
$ python pyying.py --server.host localhost --server.port 8010 --nowindow true
```
and, in another window, run mjpg-streamer
```
$ mjpg_streamer -i "/usr/local/lib/input_file.so -r -f /tmp/stream" -o     "/usr/local/lib/output_http.so -w /usr/local/www -p 8080"
```

See it in browser

http://127.0.0.1:8080/?action=stream

Spacebro API
------------

#### shoot

Send a shoot message to take picture

Optional arguments in data:

```
{
  "albumId" : "myAlbumId"
}
```

This will influence the filename in the form `snap-myAlbumId-cameraNumber.jpg`  
cameraNumber is an optional camera number defined in pyying settings.


Command line options
--------------------

#### interval

`python pyying.py --interval 15`

Shoot a picture every 15s.  
This is convenient to test running multiple instances in sync.

Tests
------------

Run tests with

```
python -m tests.test
```

## How to build docker images
it's mandatory to use:
```
COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose build
```

## How to disable `gvfs-gphoto2-volume-monitor`
In order to release the photo camera you need to disable, stop and mask service `gvfs-gphoto2-volume-monitor.service`
```
systemctl --user disable gvfs-gphoto2-volume-monitor.service
systemctl --user mask gvfs-gphoto2-volume-monitor.service
```