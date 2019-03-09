BLEA (Bluetooth advertisement) 
==============================

Description
-----------

This plugin is a plugin allowing to receive the events of some bluetooth devices (such as NIU from Nodon).

![blea icon](../images/blea_icon.png)

Configuration
-------------

Plugin configuration:
========================

a. Installation/Creation

> **Tip**
>
> In order to use the plugin, you have to download it, install it and
> activate it like any Jeedom plugin.

-   After that you will arrive on this page:

![gestion](../images/gestion.jpg)

On this page you have little to do. He is strongly recommended to start installing dependencies (even if they appear OK). Then at the end refresh the page.

> **Important**
>
> The most important thing here is to select your Bluetooth 
> controller

The other option available on this page is: ** Delete
automatically excluded devices **. This allows you to delete
Jeedom's device when excluded.

You can also check the status of the dependencies and restart them.
In case of trouble with the plugin, always relaunch the dependencies even if OK 
in case of doubt

The plugin
=========

Go to the Plugins menu &gt; Home Automation Protocol to find
the plugin.

![blea screenshot1](../images/blea_screenshot1.jpg)

On this page you will see the modules already included.

On the top part of this page, you have several buttons.

-   Inclusion button: this button allows to put Jeedom in Inclusion mode.

-   Exclusion button: this button allows to put Jeedom in Exclusion mode.

-   Bouton Configuration : ce bouton permet d’ouvrir la fenêtre de
    plugin configuration.

-   Bouton Santé : ce bouton permet d’avoir un aperçu Santé de tous
    vos modules.

![blea screenshot2](../images/blea_screenshot2.jpg)

Equipment
==========

When you click on one of your modules, you arrive on the modeule configuration page. Here, like everywhere in Jeedom you can 

on the left side:

-   Give the module a name.

-   Activate / make it visible or not.

-   Choose his parent object.

-   Give it a category.

-   Definir un delai de surveillance de communication pour
    certains modules.

-   Put a comment.

On the right side you will find:

-   Le profil de l’équipement (généralement auto détecté si le module
    le permet).

-   Choisir un modèle si pour ce profil plusieurs modèles
    sont disponibles.

-   Voir le visuel.

Quels modules 
=============

Pour le moment, seuls certains modules spécifiques sont reconnus.

Cas des NIU 
-----------

Les NIU s’incluent très facilement, mettez Jeedom en Inclusion puis
appuyer sur le bouton (aussi simple que cela).

Une fois le NIU créé, vous obtiendrez ceci :

![blea screenshot3](../images/blea_screenshot3.jpg)

Vous aurez ainsi 4 commandes :

![blea commands niu](../images/blea_commands_niu.jpg)

-   BoutonId : donne une représentation numérique du type d’appui (idéal
    pour les scénarios)

01 : simple appui

02 : double appui

03 : appui long

04 : relachement

-   Boutons : donne une représentation textuelle du type d’appui

-   Rssi : donne la valeur d’intensité du signal

-   Batterie : donne la valeur de la batterie

Case of other modules
--------------------

-   D’autres modules peuvent être inclus du type beacon NUT, bracelet
    fitbit, etc.

Ils permettront une détection de présence avec une détection sur un
créneau de 1 minute.

Of course many other modules will be added.

Changelog
---------

Detailed changelog :
<https://github.com/jeedom/plugin-blea/commits/stable>

List of compatible equipment
---------------------------------

<https://jeedom.github.io/documentation/#equipment>
