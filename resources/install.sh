touch /tmp/dependancy_blea_in_progress
echo 0 > /tmp/dependancy_blea_in_progress
echo "Launch install of blea dependancy"
sudo apt-get update
echo 50 > /tmp/dependancy_blea_in_progress
sudo apt-get install -y python-pip 
echo 66 > /tmp/dependancy_blea_in_progress
sudo apt-get install -y libglib2.0-dev git
echo 75 > /tmp/dependancy_blea_in_progress
sudo pip install pyudev
sudo pip install pyserial
cd /tmp
sudo git clone https://github.com/IanHarvey/bluepy.git
cd /tmp/bluepy
sudo python setup.py build
sudo python setup.py install
sudo connmanctl enable bluetooth
echo 100 > /tmp/dependancy_blea_in_progress
echo "Everything is successfully installed!"
rm /tmp/dependancy_blea_in_progress