# 26/06/2019
- Rajout du xiaomi cleargrass
- Rajout du lywsd02 Xiaomi
- Début de gestion dynamique de modèles
- Début réécriture gamme playbulb pour plus avoir de différence en fonction des firmwares
- Correction bug sur status démon dans certains cas
- NB : plus besoin de refresh pour les xiaomi HT les miflora : gain de batterie, meilleur portée, plus de datas. Je recommande de cliquer sur recréer les commandes pour ces devices (en choisissant ne pas supprimer)

# 22/05/2019

- Passage de la page d'équipement en V4 compliant.
- Amélioration des xiaomi hygrothermographe (plus besoin de connection pour les datas) merci @kipk
- Amélioration des miflora (plus besoin de connection pour les datas)

# 09/03/2019

- Ajout de la gestion automatique du daemon sur les antennes.
- Gestion temp négative
- Correction sur le rafraichissement des nuts (info batterie)

# 16/01/2019

- Correction d'un soucis sur le maximum possible d'une commande

# 07/06/2018

- Amélioration du script de dépendances.
- Suppressions du check dépendances qui restera vert quoiqu'il en soit en attendant (pensez lors de l'installation à lancer les dépendances)

# 06/04/2018

- Correction probable d'un bug de refresh notification sur Hygrothermographe et Miflora (necessite probablement une relance des dépendances pour les gens impactés)

# 28/03/2018

- rajout conf dreamscreen
- modification du démon pour préciser les logs
- modification de la reconnaissance des MI_SCALE V1
- Watchdog bluepy-helper (en essai)

# 10/02/2018

- Correction d'un bug sur la modal de graph réseau si jamais un équipement n'avait pas d'objet

# 01/03/2018

- Rajout de la conf pour le thermomètre/hygrometre avec écran Xiaomi
- Rajout de certaines confs awox mesh
