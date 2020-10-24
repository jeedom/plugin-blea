touch /tmp/dependancy_blea_in_progress
echo 0 > /tmp/dependancy_blea_in_progress
echo "Launch install of blea dependancy"
sudo apt-get update
echo 50 > /tmp/dependancy_blea_in_progress
sudo apt-get install -y python3-pip python-dev build-essential python-requests bluetooth libffi-dev libssl-dev
echo 66 > /tmp/dependancy_blea_in_progress
sudo apt-get install -y libglib2.0-dev git
echo 75 > /tmp/dependancy_blea_in_progress
sudo pip3 install pyudev
sudo pip3 install pyserial
sudo pip3 install requests
sudo pip3 install bluepy
echo 80 > /tmp/dependancy_blea_in_progress
sudo pip3 install cryptography
echo 90 > /tmp/dependancy_blea_in_progress
sudo pip3 install pycrypto
echo 95 > /tmp/dependancy_blea_in_progress
cd /tmp
sudo rm -R /tmp/bluepy >/dev/null 2>&1
sudo git clone https://github.com/sarakha63/bluepy.git
cd /tmp/bluepy
sudo python setup.py build
sudo python setup.py install
sudo connmanctl enable bluetooth >/dev/null 2>&1
sudo hciconfig hci0 up >/dev/null 2>&1
sudo hciconfig hci1 up >/dev/null 2>&1
sudo hciconfig hci2 up >/dev/null 2>&1
sudo rm -R /tmp/bluepy
echo 100 > /tmp/dependancy_blea_in_progress
echo "Everything is successfully installed!"
rm /tmp/dependancy_blea_in_progress
