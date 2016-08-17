touch /tmp/dependancy_blea_in_progress
echo 0 > /tmp/dependancy_blea_in_progress
echo "Launch install of blea dependancy"
sudo apt-get update
echo 50 > /tmp/dependancy_blea_in_progress
sudo apt-get install -y bluez bluez-hcidump 
echo 66 > /tmp/dependancy_blea_in_progress
sudo apt-get install -y libglib2.0-dev
echo 75 > /tmp/dependancy_blea_in_progress
sudo pip install bluepy
echo 100 > /tmp/dependancy_blea_in_progress
echo "Everything is successfully installed!"
rm /tmp/dependancy_blea_in_progress