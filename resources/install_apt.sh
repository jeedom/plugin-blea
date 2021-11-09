PROGRESS_FILE=/tmp/dependancy_blea_in_progress
if [ ! -z $1 ]; then
	PROGRESS_FILE=$1
fi
touch ${PROGRESS_FILE}
echo 0 > ${PROGRESS_FILE}
echo "********************************************************"
echo "*			 Installation des dépendances			 *"
echo "********************************************************"
sudo apt-get update
echo 20 > ${PROGRESS_FILE}
sudo apt-get install -y python3-dev build-essential python3-requests python3-setuptools python3-serial python3-pyudev bluetooth libffi-dev libssl-dev libbluetooth-dev libopenjp2-7 libtiff5 libatlas-base-dev rfkill
sudo apt-get install -y python3 bluez python3-pip --reinstall
sudo pip3 install -U setuptools
echo 40 > ${PROGRESS_FILE}
sudo apt-get install -y libglib2.0-dev git
echo 50 > ${PROGRESS_FILE}
sudo pip3 install pyudev
sudo pip3 install pyserial
sudo pip3 install requests
sudo pip3 install pybluez
sudo pip3 install pillow
sudo pip3 install numpy
sudo pip3 install bluepy
echo 60 > ${PROGRESS_FILE}
cd /tmp
sudo rm -R /tmp/bluepy >/dev/null 2>&1
sudo git clone https://github.com/IanHarvey/bluepy.git
cd /tmp/bluepy
sudo python3 setup.py build
sudo python3 setup.py install
sudo connmanctl enable bluetooth >/dev/null 2>&1
sudo rfkill unblock 0 >/dev/null 2>&1
sudo rfkill unblock 1 >/dev/null 2>&1
sudo rfkill unblock 2 >/dev/null 2>&1
sudo hciconfig hci0 up >/dev/null 2>&1
sudo hciconfig hci1 up >/dev/null 2>&1
sudo hciconfig hci2 up >/dev/null 2>&1
sudo rm -R /tmp/bluepy
cd /tmp
echo 85 > ${PROGRESS_FILE}
sudo pip3 install cryptography
echo 90 > ${PROGRESS_FILE}
sudo pip3 install pycrypto
echo 100 > ${PROGRESS_FILE}
echo "********************************************************"
echo "*			 Installation terminée					*"
echo "********************************************************"
rm ${PROGRESS_FILE}
