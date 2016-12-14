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
    require_once dirname(__FILE__) . '/../class/dotti.class.php';
    include_file('core', 'authentification', 'php');

    if (!isConnect('admin')) {
        throw new Exception(__('401 - Accès non autorisé', __FILE__));
    }
	
	if (init('action') == 'loadImage') {
		$name = init('name');
		ajax::success(dottiblea::loadImage($name));
	}
	
	if (init('action') == 'renameImage') {
		$oriname = init('oriname');
		$newname = init('newname');
		ajax::success(dottiblea::renameImage($oriname,$newname));
	}
	
	if (init('action') == 'saveImage') {
		$id = init('id');
		if ($id ==''){
			$id = eqLogic::byType('dotti')[0]->getId();
		}
		log::add('dotti','debug',print_r(eqLogic::byType('dotti'),true));
		$name = init('name');
		$data = init('data');
		if ($name == ''){
			ajax::error('Veuillez choisir un nom pour votre image');
		} else {
			ajax::success(dottiblea::saveImage($id,$name,$data));
		}
	}
	
	if (init('action') == 'saveImagejson') {
		$id = init('id');
		$name = init('name');
		$data = init('data');
		if ($name == ''){
			ajax::error('Veuillez choisir un nom pour votre image');
		} else {
			ajax::success(dottiblea::saveImage($id,$name,$data,true));
		}
	}
	
	if (init('action') == 'delImage') {
		$name = init('name');
		ajax::success(dottiblea::delImage($name));
	}
	
	if (init('action') == 'loadMemoryList') {
		ajax::success(dottiblea::listMemory());
	}
	
	if (init('action') == 'sendPixelArray') {
		$array = init('array');
		$id = init('id');
		if ($id ==''){
			$id = eqLogic::byType('blea')[0]->getId();
		}
		ajax::success(dottiblea::sendDataRealTime($array,$id));
	}
	
	if (init('action') == 'getImageCode') {
		$name = init('name');
		ajax::success(dottiblea::getImageCode($name));
	}
	
	if (init('action') == 'loadImageCode') {
		$name = init('name');
		$data = init('data');
		ajax::success(dottiblea::loadImageCode($name,$data));
	}

    throw new Exception(__('Aucune méthode correspondante à : ', __FILE__) . init('action'));
    /*     * *********Catch exeption*************** */
} catch (Exception $e) {
    ajax::error(displayExeption($e), $e->getCode());
}
?>
