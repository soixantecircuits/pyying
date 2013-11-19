Simple application that turn a camera into an IP camera, and takes pictures with OSC command.

Install instructions to be updated soon.

```

sudo apt-get install python-pygame python-pip gphoto2 libgphoto2-2-dev libgphoto2-port0
sudo pip install pyOSC

cd ~/sources
mkdir python
mkdir python/soixante
cd python/soixante
git clone git@github.com:soixantecircuits/pyying.git
cd pyying
mkdir /tmp/stream
python pyying.py
```
