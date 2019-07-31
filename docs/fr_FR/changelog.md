# 30/07/2019
- Correction d'un bug sur le dotti lié au passage à python3

# 29/07/2019
- Fixes mineurs
- Séparation des équipements inconnus sur la page d'équipement
- Possibilité de supprimer tous les équipements inconnus en un clic (uniquement ceux non attribués à un objet)
- Correction d'un bug sur le scan sélectif "Inconnu"
- Améliorations globales

# 20/07/2019
- Changement de méthode pour l'ensemble de la gamme playbulb (une seule conf et des visuels) plus de dépendances par rapport aux différentes versions (maintenant a l'inclusion on récupère les adresses des différentes méthodes)
- Rajout de la miscale V2 avec poids et impédance (et tout un tas de mesures calculées). Gestion des utilisateurs pour les calculs (dans le bouton configuration avancée)
- Changement de la miscale V1 (il faudra recréer les utilisateurs) mais on gagne quelques infos en plus
- Pour les playbulbs je recommande une ré-inclusion de tous les équipements
- Correction d'un bug sur le graphe réseau en mode sans local
- Correction d'un bug sur la régénération des commandes sur demande
- A l'inclusion les antennes d'émissions et de réceptions sont automatiquement remplies par l'antenne ayant permis l'inclusion
- Changement de la notion de présence (plus besoin de repetion toujours, plus besoin de return state et return state time) maintenant une commande présence par antenne et local et une commande présence dépéndant des autres
- Réglage possible maintenant du scan intervalle et du nombre de scans où un équipement n'est pas visible pour le déclarer absent (gain de détection présence et surtout absence)
- Possibilité de mettre à jour toutes les antennes en un clic
- Possibilité de redémarrer toutes les antennes en un clic
- Lors d'une mise à jour du plugin les antennes sont mises à jour et redémarrer (peut parfois échouer)
- Passage en scan passif sauf au learn (avec mémoire de la conf Jeedom pour savoir qui est qui)
- Passage à Python3
- Modification perso de bluepy, avec meilleurs gestion d'erreur (peut être plus de blocage sur Proxmox, VMware)
- Rajout d'un délai de connexion au sein même de bluepy pour éviter qu'une tentative de connexion tourne en boucle
- Si le démon Local est en status NOK alors les présences locales sont mises a 0
- Si une antenne n'a pas communiqué depuis plus d'une minute alors les présences de cette antenne sont mises à 0
- Rajout de la possibilité de récupérer les nouvelles configurations sans mettre à jour le plugin
- Rajout d'un mode passif ou actif pour le scan
- Réorganisation de la page équipement
- Rajout d'une option nombre de scan pour considérer absent spécifique à l'équipement (si défini remplacera la globale pour cet équipement)
- Ajout de la possibilité de définir en un clic tous les équipements sur une antenne ou sur local
- Possibilité de choisir exactement le type de produit à inclure lors d'un scan (avec possibilité de choisir tous)

# 26/06/2019
- Rajout du Xiaomi Cleargrass
- Rajout du lywsd02 Xiaomi
- Début de gestion dynamique de modèles
- Début réécriture gamme playbulb pour plus avoir de différence en fonction des firmwares
- Correction bug sur status démon dans certains cas
- Déblocage des fonctions rafraîchissement / délai : chaque utilisateur fait ce qu'il veut (attention quand même)
- NB : plus besoin de rafraîchissement pour les Xiaomi HT les miflora : gain de batterie, meilleur portée, plus de datas. Je recommande de ne pas activer le rafraîchissement forcé qui n'est plus nécessaire sauf si votre équipement semble ne pas advertiser correctement

# 22/05/2019

- Passage de la page d'équipement en conformité V4.
- Amélioration des Xiaomi hygrothermomètre (plus besoin de connexion pour les datas) merci @kipk
- Amélioration des miflora (plus besoin de connexion pour les datas)

# 09/03/2019

- Ajout de la gestion automatique du démon sur les antennes.
- Gestion température négative
- Correction sur le rafraîchissement des nuts (info batterie)

# 16/01/2019

- Correction d'un soucis sur le maximum possible d'une commande

# 07/06/2018

- Amélioration du script de dépendances.
- Suppressions de la vérification des dépendances qui restera verte quoiqu'il en soit en attendant (pensez lors de l'installation à lancer les dépendances)

# 06/04/2018

- Correction probable d'un bug de rafraîchissement de notification sur hygrothermomètre et Miflora (nécessite probablement une relance des dépendances pour les gens impactés)

# 28/03/2018

- rajout conf dreamscreen
- modification du démon pour préciser les logs
- modification de la reconnaissance des MI_SCALE V1
- Watchdog bluepy-helper (en essai)

# 10/02/2018

- Correction d'un bug sur la modal de graphe réseau si jamais un équipement n'avait pas d'objet

# 01/03/2018

- Rajout de la conf pour le thermomètre/hygromètre avec écran Xiaomi
- Rajout de certaines configurations Awox mesh