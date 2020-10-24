#!/bin/bash

# Automatically generated script by
# vagrantbox/doc/src/vagrant/src-vagrant/deb2sh.py
# The script is based on packages listed in debpkg_minimal.txt.

#set -x  # make sure each command is printed in the terminal
echo "Lancement de la synchronisation des configurations"
echo "Déplacement dans le répertoire de travail"
cd /tmp
echo "Récupération des sources (cette étape peut durer quelques minutes)"
rm -rf /tmp/plugin-blea > /dev/null 2>&1
sudo git clone --depth=1 https://github.com/Ermax81/plugin-blea.git
if [ $? -ne 0 ]; then
    echo "Unable to fetch Jeedom Blea git.Please check your internet connexion and github access"
    exit 1
fi
BASEDIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
if [ -d  ${BASEDIR}/../core/config/devices ]; then
	echo "Suppression des configurations Jeedom existantes"
	sudo rm -rf ${BASEDIR}/../core/config/devices/*
	echo "Copie des nouvelles configurations Jeedom"
	cd /tmp/plugin-blea/core/config/devices
	ls $1 | while read x; do echo $x; done
	sudo mv * ${BASEDIR}/../core/config/devices/
	echo "Suppression des configurations Blea python existantes"
	sudo rm -rf ${BASEDIR}/../resources/blead/devices/*
	echo "Copie des nouvelles configurations Blea Python"
	cd /tmp/plugin-blea/resources/blead/devices
	ls $1 | while read x; do echo $x; done
	sudo mv * ${BASEDIR}/../resources/blead/devices/
	echo "Nettoyage du répertoire de travail"
	sudo rm -R /tmp/plugin-blea
	sudo chown -R www-data:www-data ${BASEDIR}/../resources/blead/devices/
	sudo chown -R www-data:www-data ${BASEDIR}/../core/config/devices/
	echo "Vos configurations sont maintenant à jour !"
	echo "Le démon va se relancer, vous pouvez fermer cette fenêtre"
else
	echo 'Veuillez installer les dépendances'
fi
