sudo apt-get install libjpeg62-dev imagemagick subversion
sudo apt-get install python-pygame python-pip gphoto2 libgphoto2-2-dev libgphoto2-port0
# sudo pip install --allow-unverified pyOSC

cd ../
git clone https://github.com/ptone/pyosc
cd pyosc
sudo ./setup.py install
cd ../pyying

svn co https://svn.code.sf.net/p/mjpg-streamer/code/mjpg-streamer
cd mjpg-streamer
make
sudo make install
