Simple application that turn a camera into an IP camera, and takes pictures with OSC command.

Install instructions to be updated soon.

```
sudo apt-get install subversion autotools-dev autoconf libtool autopoint libpopt-dev python-pygame python-pip
svn co https://gphoto.svn.sourceforge.net/svnroot/gphoto/trunk gphoto
cd gphoto/libgphoto2
autoreconf --install --symlink
./configure --with-prefix=/usr --with-camlibs=canon
make
sudo make install

cd ../gphoto2
autoreconf -is
./configure --with-libgphoto2=/usr
make
sudo make install
sudo mv /usr/local/lib/libgphoto2* /usr/lib

cd ~/sources
mkdir python
mkdir python/soixante
cd python/soixante
sudo pip install pyOSC
cd pyying
mkdir /tmp/stream
python previewstream.py
```
