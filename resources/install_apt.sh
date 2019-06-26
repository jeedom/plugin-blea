PROGRESS_FILE=/tmp/dependancy_blea_in_progress
if [ ! -z $1 ]; then
	PROGRESS_FILE=$1
fi
touch ${PROGRESS_FILE}
echo 0 > ${PROGRESS_FILE}
echo "********************************************************"
echo "*             Installation des dépendances             *"
echo "********************************************************"
sudo apt-get update
echo 50 > ${PROGRESS_FILE}
sudo apt-get install -y python-pip python-dev build-essential python-requests bluetooth libffi-dev libssl-dev
echo 66 > ${PROGRESS_FILE}
sudo apt-get install -y libglib2.0-dev git
echo 75 > ${PROGRESS_FILE}
sudo pip install pyudev
sudo pip install pyserial
sudo pip install requests
sudo pip install -U pip setuptools
sudo curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python get-pip.py --force-reinstall
echo 80 > ${PROGRESS_FILE}
cd /tmp
sudo rm -R /tmp/bluepy >/dev/null 2>&1
sudo git clone https://github.com/IanHarvey/bluepy.git
cd /tmp/bluepy
sudo python setup.py build
sudo python setup.py install
sudo connmanctl enable bluetooth >/dev/null 2>&1
sudo hciconfig hci0 up >/dev/null 2>&1
sudo hciconfig hci1 up >/dev/null 2>&1
sudo hciconfig hci2 up >/dev/null 2>&1
sudo rm -R /tmp/bluepy
cd /tmp
echo 85 > ${PROGRESS_FILE}
sudo pip install cryptography
echo 90 > ${PROGRESS_FILE}
sudo pip install pycrypto
echo 100 > ${PROGRESS_FILE}
echo "********************************************************"
echo "*             Installation terminée                    *"
echo "********************************************************"
rm ${PROGRESS_FILE}