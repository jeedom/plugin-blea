# 20/07/2019
- Changement de méthode pour l'ensemble de la gamme playbulb (une seule conf et des visuels) plus de dépendances par rapport aux différentes versions (maintenant a l'inclusion on récupére les adresses des diffférentes méthodes)
- Rajout de la miscale V2 avec poids et impedance (et tout un tas de mesures calculées). Gestion des utilisateurs pour les calculs (dans le bouton config avancée)
- Changement de la miscale V1 (il faudra recréer les users) mais on gagne quelques infos en plus
- Pour les playbulbs je recommande une reinclusion de tous les devices
- Correction d'un bug sur le graph réseau en mode sans local
- Correction d'un bug sur la régénération des commandes sur demande
- A l'inclusion les antennes d'émissions et de réceptions sont automatiquement remplies par l'antenne ayant permis l'inclusion
- Changement de la notion de présence (plus besoin de repetion toujours, plus besoin de return state et return state time) maintenant une commande présence par antenne et local et une command presence dependant des autres
- Réglage possible maintenant du scan interval et du nombre de scan ou un device n'est pas visible pour le déclarer absent (gain de détection présence et surtout absence)
- Possibilité de mettre à jour toutes les antennes en un clic
- Possibilité de redémarrer toutes les antennes en un clic
- Lors d'une mise à jour du plugin les antennes sont mises à jour et redémarrer (peut parfois échouer)
- Passage en scan passif sauf au learn (avec mémoire de la conf jeedom pour savoir qui est qui)
- Passage à Python3
- Modification perso de bluepy, avec meilleurs gestion d'erreur (peut etre plus de blocage sur proxmow, vmware)
- Rajout d'un timeout de connection au sein meme de bluepy pour éviter qu'une tentative de connection tourne en boucle
- Si le démon Local est en status NOK alors les présences locales sont mises a 0
- Si une antenne n'a pas communiqué depuis plus d'une minute alors les présences de cette antenne sont mises à 0
- Rajout de la possibilité de récupérer les nouvelles configurations sans mettre à jour le plugin
- Rajout d'un mode passif ou actif pour le scan
- Réorganisation de la page équipement
- Rajout d'une option nombre de scan pour considérer absent spécifique à l'équipement (si défini remplacera la globale pour cet équipement)

# 26/06/2019
- Rajout du xiaomi cleargrass
- Rajout du lywsd02 Xiaomi
- Début de gestion dynamique de modèles
- Début réécriture gamme playbulb pour plus avoir de différence en fonction des firmwares
- Correction bug sur status démon dans certains cas
- Deblocage des fonctions refresh / delai : chaque user fait ce qu'il veut (attention quand même)
- NB : plus besoin de refresh pour les xiaomi HT les miflora : gain de batterie, meilleur portée, plus de datas. Je recommande de ne pas activer le refresh forcé qui n'est plus necessaire sauf si votre device semble ne pas advertiser correctement

# 22/05/2019

- Passage de la page d'équipement en V4 compliant.
- Amélioration des xiaomi hygrothermographe (plus besoin de connection pour les datas) merci @kipk
- Amélioration des miflora (plus besoin de connection pour les datas)

# 09/03/2019

- Added automatic daemon management on antennas.
- Negative temp management
- Correction sur le rafraichissement des nuts (info batterie)

# 16/01/2019

- Correction d'un soucis sur le maximum possible d'une commande

# 07/06/2018

- Amélioration du script de dépendances.
- Suppressions du check dépendances qui restera vert quoiqu'il en soit en attendant (pensez lors de l'installation à lancer les dépendances)

# 06/04/2018

- Fix a refresh notification bug on Hygrothermograph and Miflora (probably needs relaunching of dependencies for impacted people)

# 28/03/2018

- rajout conf dreamscreen
- modification du démon pour préciser les logs
- modification de la reconnaissance des MI_SCALE V1
- Watchdog bluepy-helper (en essai)

# 10/02/2018

- Fixed a bug on the network graph modal if a device had no object

# 01/03/2018

- Rajout de la conf pour le thermomètre/hygrometre avec écran Xiaomi
- Rajout de certaines confs awox mesh
