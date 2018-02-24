Installation for Debian web server


* sudo apt-get install python-pip curl autoconf libtool libexpat1 libexpat1-dev zlib1g-dev libboost-dev libboost-test-dev apache2
* pip install pykml
* pip install python-xmp-toolkit
* pip install -U googlemaps

* cd ~
* git clone https://github.com/google/protobuf.git
* cd protobuf
* ./autogen.sh
* ./configure && make && sudo make install
* cd python
* python setup.py build
* sudo python setup.py install

* cd ~
* git clone git://anongit.freedesktop.org/git/exempi.git 
* cd exempi
* patch -p1 < ~/kmz2gevr/exempi.patch
* ./autogen.sh
* ./configure && make && sudo make install

* add the following to /etc/profile:

>export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH


* cd ~
* git clone https://github.com/kbogert/kmz2gevr.git
* cd kmz2gevr
* sudo python setup.py install

* cd /etc/apache2/mods-enabled
* sudo ln -s ../mods-available/cgi.load cgi.load
* edit /etc/apache2/sites-enabled/000-default.conf , add:

>ScriptAlias "/cgi-bin/" "/var/www/cgi-bin/"

>PassEnv PYTHONPATH

* sudo service apache2 restart
* sudo mkdir /var/www/cgi-bin
* cd ~/kmz2gevr
* sudo cp kmz2gevr_cgi.py /var/www/cgi-bin/
* sudo cp upload.html upload.html /var/www/html


* install a google api key with access to the elevation api into /usr/local/lib/pythonX.X/dist-packages/kmz2gevr/googleapi.key

