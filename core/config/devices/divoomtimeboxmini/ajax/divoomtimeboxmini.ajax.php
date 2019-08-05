<?php

/* This file is part of Jeedom.
 *
 * Jeedom is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Jeedom is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Jeedom. If not, see <http://www.gnu.org/licenses/>.
 */

try {
    require_once dirname(__FILE__) . '/../../../../../../../core/php/core.inc.php';
    require_once dirname(__FILE__) . '/../class/divoomtimeboxmini.class.php';
    include_file('core', 'authentification', 'php');

    if (!isConnect('admin')) {
        throw new Exception(__('401 - Accès non autorisé', __FILE__));
    }

	if (init('action') == 'loadImage') {
		$name = init('name');
		ajax::success(divoomtimeboxminiblea::loadImage($name));
	}

  if (init('action') == 'sendFiles') {
		ajax::success(divoomtimeboxminiblea::sendFiles());
	}

	if (init('action') == 'renameImage') {
		$oriname = init('oriname');
		$newname = init('newname');
		ajax::success(divoomtimeboxminiblea::renameImage($oriname,$newname));
	}

  if (init('action') == 'renameImageFile') {
		$oriname = init('oriname');
		$newname = init('newname');
		ajax::success(divoomtimeboxminiblea::renameImage($oriname,$newname,True));
	}

	if (init('action') == 'saveImage') {
		$id = init('id');
		if ($id ==''){
			$id = eqLogic::byType('divoomtimeboxmini')[0]->getId();
		}
		log::add('divoomtimeboxmini','debug',print_r(eqLogic::byType('divoomtimeboxmini'),true));
		$name = init('name');
		$data = init('data');
		if ($name == ''){
			ajax::error('Veuillez choisir un nom pour votre image');
		} else {
			ajax::success(divoomtimeboxminiblea::saveImage($id,$name,$data));
		}
	}

	if (init('action') == 'saveImagejson') {
		$id = init('id');
		$name = init('name');
		$data = init('data');
		if ($name == ''){
			ajax::error('Veuillez choisir un nom pour votre image');
		} else {
			ajax::success(divoomtimeboxminiblea::saveImage($id,$name,$data,true));
		}
	}

	if (init('action') == 'delImage') {
		$name = init('name');
		ajax::success(divoomtimeboxminiblea::delImage($name));
	}

	if (init('action') == 'loadMemoryList') {
		ajax::success(divoomtimeboxminiblea::listMemory());
	}

	if (init('action') == 'sendPixelArray') {
		$array = init('array');
		$id = init('id');
		if ($id ==''){
			$id = eqLogic::byType('blea')[0]->getId();
		}
		ajax::success(divoomtimeboxminiblea::sendDataRealTime($array,$id));
	}

	if (init('action') == 'getImageCode') {
		$name = init('name');
		ajax::success(divoomtimeboxminiblea::getImageCode($name));
	}

	if (init('action') == 'loadImageCode') {
		$name = init('name');
		$data = init('data');
		ajax::success(divoomtimeboxminiblea::loadImageCode($name,$data));
	}

	if (init('action') == 'fileupload') {
		$uploaddir = __DIR__ . '/../../../../../data/divoomtimeboxmini';
		if (!file_exists($uploaddir)) {
			mkdir($uploaddir);
		}
		if (!file_exists($uploaddir)) {
			throw new Exception(__('Répertoire de téléversement non trouvé : ', __FILE__) . $uploaddir);
		}
		if (!isset($_FILES['file'])) {
			throw new Exception(__('Aucun fichier trouvé. Vérifiez le paramètre PHP (post size limit)', __FILE__));
		}
		$extension = strtolower(strrchr($_FILES['file']['name'], '.'));
		if (!in_array($extension, array('.gif','.bmp','.png'))) {
			throw new Exception('Extension du fichier non valide (autorisé .gif .bmp .png) : ' . $extension);
		}
		if (filesize($_FILES['file']['tmp_name']) > 50000) {
			throw new Exception(__('Le fichier est trop gros (maximum 50ko)', __FILE__));
		}
		if (!move_uploaded_file($_FILES['file']['tmp_name'], $uploaddir . '/' . $_FILES['file']['name'])) {
			throw new Exception(__('Impossible de déplacer le fichier temporaire', __FILE__));
		}
		if (!file_exists($uploaddir . '/' . $_FILES['file']['name'])) {
			throw new Exception(__('Impossible de téléverser le fichier (limite du serveur web ?)', __FILE__));
		}
		divoomtimeboxminiblea::refreshTitles();
		ajax::success();
	}

	if (init('action') == 'delImageFile') {
		$name = init('name');
		ajax::success(divoomtimeboxminiblea::delImage($name,True));
	}

    throw new Exception(__('Aucune méthode correspondante à : ', __FILE__) . init('action'));
    /*     * *********Catch exeption*************** */
} catch (Exception $e) {
    ajax::error(displayExeption($e), $e->getCode());
}
?>
