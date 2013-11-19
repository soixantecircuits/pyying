#Pying

Simple application that turn a camera into an IP camera, and takes pictures with OSC command.


#Install pyying

##On a MAC (Maverick)

You need (brew)[http://brew.sh/] or copy paste :
`ruby -e "$(curl -fsSL https://raw.github.com/mxcl/homebrew/go)"`

Make sure you have:

`xcode-select --install` as it seems Apple make some joke with last command line tools.

Read there : 
http://www.pygame.org/download.shtml
and here also :
https://bitbucket.org/pygame/pygame/issue/82/homebrew-on-leopard-fails-to-install#comment-627494

Then, let's roll it:

```
brew update && brew upgrade

brew tap homebrew/headonly
brew tap samueljohn/python

sudo easy_install pip
pip-2.7 install nose

brew install --HEAD smpeg
brew install --universal libtool
brew install --universal libusb
brew install gphoto2 hg python sdl sdl_image sdl_mixer sdl_ttf portmidi 
brew install pygame
```


##On Linux

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

_Usefull for gdb : http://panks.me/blog/2013/11/install-gdb-on-os-x-mavericks-from-source/_

##Install mjpg-streamer


With mjpg-streamer, you can convert the jpeg stream from pyying to a MJPEG stream, that can be read in a browser

###On linux
```
sudo apt-get install libjpeg62-dev subversion
```
###On Mac
```
brew install libjpeg62-dev
```

And then:

```
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
