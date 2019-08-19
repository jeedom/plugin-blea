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

/* * ***************************Includes********************************* */
require_once dirname(__FILE__) . '/../../../../../../../core/php/core.inc.php';

class divoompixooblea extends blea {

	public static function array2table($_array) {
		$return = '<table>';
		foreach ($_array as $x => $line) {
			$return .= '<tr>';
			foreach ($line as $y => $color) {
				$return .= '<td style="Background-Color:RGB(' . $color[0] . ',' . $color[1] . ',' . $color[2] . ');height:40px;width:40px;"></td>';
			}
			$return .= '</tr>';
		}
		$return .= '<table>';
		return $return;
	}

	public static function sendDataRealTime($_data, $_id) {
		$divoompixoo = blea::byId($_id);
		$data = array();
		foreach ($_data as $pixel => $color) {
			$data[$pixel] = hex2rgb($color);
		}

		$cmd = $divoompixoo->getCmd('action','name:divoompixoo,classlogical:loadimage,type:display,value:calcul');
		if (is_object($cmd)){
			$cmd->execute(array('title' => $data));
		}
	}

	public static function sendFiles() {
		log::add('blea','info','Sending Divoom files on remotes ...');
		$remotes = blea_remote::all();
		$image_path = dirname(__FILE__) . '/../../../../../data/';
		log::add('blea','info','Compression du dossier local');
		exec('tar -zcvf /tmp/divoom-image.tar.gz ' . $image_path);
		foreach ($remotes as $remote) {
			log::add('blea','info','Envoie du fichier  /tmp/folder-blea.tar.gz');
			$result = false;
			$result = $remote->execCmd(['rm -Rf /var/www/html/plugins/blea/data','mkdir -p /var/www/html/plugins/blea/data']);
			if ($remote->sendFiles('/tmp/divoom-image.tar.gz','/var/www/html/plugins/blea/data/divoom-image.tar.gz')) {
				log::add('blea','info',__('Décompression du dossier distant',__FILE__));
				$result = $remote->execCmd(['tar -zxf /var/www/html/plugins/blea/data/divoom-image.tar.gz -C /var/www/html/plugins/blea/','rm /var/www/html/plugins/blea/data/divoom-image.tar.gz']);
			}
		}
		log::add('blea','info',__('Suppression du zip local',__FILE__));
		exec('rm /tmp/divoom-image.tar.gz');
		log::add('blea','info',__('Finie',__FILE__));
		return $result;

	}

	public static function loadImage($_name) {
		$file = dirname(__FILE__) . '/../../../../../data/collection_divoompixoo.json';
		$dataColor = array();
		if (file_exists($file)) {
			$dataMemory = json_decode(file_get_contents($file), true);
			if (isset($dataMemory[$_name])) {
				$dataColor = $dataMemory[$_name];
			}
		}
		return $dataColor;
	}

	public static function renameImage($_oriname, $_newname,$_file =False) {
		if ($_file){
			$file = dirname(__FILE__) . '/../../../../../data/divoompixoo/'.$_oriname;
			$extension = pathinfo($file, PATHINFO_EXTENSION);
			$new = dirname(__FILE__) . '/../../../../../data/divoompixoo/'.$_newname.'.'.$extension;
			rename($file,$new);
		} else {
			$file = dirname(__FILE__) . '/../../../../../data/collection_divoompixoo.json';
			if (file_exists($file)) {
				$dataMemory = json_decode(file_get_contents($file), true);
				if (isset($dataMemory[$_oriname])) {
					$oldData = $dataMemory[$_oriname];
					unset($dataMemory[$_oriname]);
					$dataMemory[strtolower($_newname)] = $oldData;
				}
			}
			ksort($dataMemory);
			if (file_exists($file)) {
				shell_exec('sudo rm ' . $file);
			}
			file_put_contents($file, json_encode($dataMemory, JSON_FORCE_OBJECT));
		}
		divoompixooblea::refreshTitles();
		return;
	}

	public static function getImageCode($_name) {
		$file = dirname(__FILE__) . '/../../../../../data/collection_divoompixoo.json';
		$dataColor = array();
		if (file_exists($file)) {
			$dataMemory = json_decode(file_get_contents($file), true);
			if (isset($dataMemory[$_name])) {
				$dataColor = $dataMemory[$_name];
			}
		}
		return json_encode($dataColor, JSON_FORCE_OBJECT);
	}

	public static function delImage($_name,$_file =False) {
		if ($_file) {
			$file = dirname(__FILE__) . '/../../../../../data/divoompixoo/'.$_name;
			unlink($file);
		} else {
			$file = dirname(__FILE__) . '/../../../../../data/collection_divoompixoo.json';
			if (file_exists($file)) {
				$dataMemory = json_decode(file_get_contents($file), true);
				if (isset($dataMemory[$_name])) {
					unset($dataMemory[$_name]);
				}
			}
			if (file_exists($file)) {
				shell_exec('sudo rm ' . $file);
			}
			file_put_contents($file, json_encode($dataMemory, JSON_FORCE_OBJECT));
		}
		divoompixooblea::refreshTitles();
		return;
	}

	public static function listMemory() {
		$file = dirname(__FILE__) . '/../../../../../data/collection_divoompixoo.json';
		$dataMemory = array();
		if (file_exists($file)) {
			$dataMemory = json_decode(file_get_contents($file), true);
		}
		$list = '';
		foreach ($dataMemory as $name => $data) {
			$list .= '<option value="' . strtolower($name) . '">' . ucfirst($name) . '</option>';
		}
		$count =0;
		$dir = dirname(__FILE__) . '/../../../../../data/divoompixoo';
		foreach (ls($dir, '*') as $file) {
			$count+=1;
		}
		return array($list,$count);
	}

	public static function getImageData($_name) {
		$file = dirname(__FILE__) . '/../../../../../data/collection_divoompixoo.json';
		$dataMemory = array();
		if (file_exists($file)) {
			$dataMemory = json_decode(file_get_contents($file), true);
		}
		$dataColor = array();
		foreach ($dataMemory as $name => $data) {
			if (strtolower($_name) == strtolower($name)) {
				foreach ($data as $pixel => $color) {
					$dataColor[$pixel] = hex2rgb($color);
				}
				break;
			}
		}
		return $dataColor;
	}

	public static function saveImage($_id, $_name, $_data, $_isjson = false) {
		try {
			divoompixooblea::sendDataRealTime($_data, $_id);
		} catch (Exception $e) {
		}
		$directory = dirname(__FILE__) . '/../../../../../data/';
		if (!is_dir($directory)) {
			mkdir($directory);
		}
		$file = dirname(__FILE__) . '/../../../../../data/collection_divoompixoo.json';
		$dataMemory = array();
		if (file_exists($file)) {
			$dataMemory = json_decode(file_get_contents($file), true);
		}
		if ($_isjson) {
			$_data = json_decode($_data, true);
		}
		$dataMemory[strtolower($_name)] = $_data;
		ksort($dataMemory);
		if (file_exists($file)) {
			shell_exec('sudo rm ' . $file);
		}
		file_put_contents($file, json_encode($dataMemory, JSON_FORCE_OBJECT));
		divoompixooblea::refreshTitles();
	}

	public static function refreshTitles() {
		$file = dirname(__FILE__) . '/../../../../../data/collection_divoompixoo.json';
		$dataMemory = array();
		if (file_exists($file)) {
			$dataMemory = json_decode(file_get_contents($file), true);
		}
		ksort($dataMemory);
		$array = array();
		foreach ($dataMemory as $name => $data) {
			$array[] = $name;
		}
		$dir = dirname(__FILE__) . '/../../../../../data/divoompixoo';
		foreach (ls($dir, '*') as $file) {
			$array[] = $file;
		}
		foreach (blea::all() as $blea) {
			if ($blea->getConfiguration('device') == 'divoompixoo'){
				$cmd = $blea->getCmd('action', 'name:divoompixoo,classlogical:loadimage,type:display,value:calcul');
				$cmd->setDisplay('title_possibility_list', json_encode($array));
				$cmd->save();
				$blea->refreshWidget();
			}
		}
	}

	public static function postSaveChild($_eqLogic) {
		divoompixooblea::refreshTitles($_eqLogic);
	}

	public static function sendData( $_eqLogic,$_type, $_data) {
		if ($_type == 'display') {
			if (isset($_data[0]) && is_array($_data[0])) {
				$data = array();
				$i = 1;
				foreach ($_data as $x => $line) {
					foreach ($line as $y => $color) {
						$data[$i] = $color;
						$i++;
					}
				}
				$_data = $data;
			}
		}
		if ($_type == 'color') {
			$arraycolor = array();
			$i = 1;
			while ($i<257){
				$arraycolor[$i] = $_data;
				$i++;
			}
			$_data = $arraycolor;
		}
		$value = array('type' => 'display', 'data' => $_data);
		return $value;
	}

	public static function convertHtml($_eqLogic,$_version = 'dashboard') {
		$replace = $_eqLogic->preToHtml($_version);
		if (!is_array($replace)) {
			return $replace;
		}
		$version = jeedom::versionAlias($_version);
		foreach ($_eqLogic->getCmd('info') as $cmd) {
			$replace['#' . $cmd->getConfiguration('logicalwidget') . '#'] = $cmd->execCmd();
			$replace['#' . $cmd->getConfiguration('logicalwidget') . '_id#'] = $cmd->getId();
			if ($cmd->getIsHistorized() == 1) {
				$replace['#' . $cmd->getConfiguration('logicalwidget') . '_history#'] = 'history cursor';
			}
		}
		foreach ($_eqLogic->getCmd('action') as $cmd) {
			$replace['#cmd_' . $cmd->getConfiguration('logicalwidget') . '_id#'] = $cmd->getId();
			if ($cmd->getConfiguration('logicalwidget') == 'loadimage') {
				$replace['#loadimage#'] = str_replace(array("'", '+'), array("\'", '\+'), $cmd->getDisplay('title_possibility_list'));
			}
		}
		return $_eqLogic->postToHtml($_version, template_replace($replace, getTemplate('core', $version, 'divoompixoo', 'blea')));
	}

	public static function calculateOutputValue($_eqLogic,$_data,$_options=null) {
		$return =array();
		$logicalid = $_data['classlogical'];
		if (in_array($logicalid,array('sendcolor','sendcolorBlink'))) {
			$return = self::sendData($_eqLogic,'color', hex2rgb($_options['color']));
		}
		elseif ($logicalid == 'blackscreen') {
			$_data['type'] = 'blackscreen';
		}
		elseif ($logicalid == 'loadimage') {
			$options = arg2array($_options['message']);
			if (isset($options['blink']) && $options['blink'] == 1) {
				$_data['blink'] = 1;
			}
			if (is_array($_options['title'])) {
				$return=array('type' => 'display', 'data' => $_options['title']);
			}
			else if (strpos($_options['title'],'.gif') !== false) {
				$path = dirname(__FILE__) . '/../../../../../data/divoompixoo/'.$_options['title'];
				$return=array('type' => 'displaydynamic', 'path' => $path);
			} else if (strpos($_options['title'],'.png') !== false || strpos($_options['title'],'.bmp') !== false) {
				$path = dirname(__FILE__) . '/../../../../../data/divoompixoo/'.$_options['title'];
				$return=array('type' => 'display', 'path' => $path);
			} else {
				$return = self::sendData($_eqLogic,'display', self::getImageData($_options['title']));
			}
		}
		elseif ($logicalid == 'lastimage') {
			$return = $_eqLogic->getCache('previousDisplay');
		}
		elseif ($logicalid == 'sendrandom') {
			$arrayicon = array();
			$arraycheck = array();
			$file = dirname(__FILE__) . '/../../../../../data/collection_divoompixoo.json';
			$dataMemory = array();
			if (file_exists($file)) {
				$dataMemory = json_decode(file_get_contents($file), true);
			}
			foreach ($dataMemory as $name => $data) {
				$arraycheck[] = $name;
			}
			$dir = dirname(__FILE__) . '/../../../../../data/divoompixoo';
			foreach (ls($dir, '*') as $file) {
				$arraycheck[] = $file;
			}
			$arrayadd = array();
			$arraydel = array();
			if ($_options['message'] != '') {
				$arrayName = explode(';', $_options['message']);
				foreach ($arrayName as $name) {
					if (substr($name, 0, 1) == '-') {
						$arraydel[] = strtolower(substr($name, 1));
					} else {
						$arrayadd[] = strtolower($name);
					}
				}
				$i = 0;
				foreach ($arraycheck as $icon) {
					if (count($arrayadd > 0)) {
						foreach ($arrayadd as $add) {
							if (strpos($icon, $add) !== false) {
								$arrayicon[] = $icon;
							}
						}
					}
					if (count($arraydel > 0)) {
						foreach ($arraydel as $del) {
							if (strpos($icon, $del) === false) {
								$arrayicon[] = $icon;
							}
						}
					}
					$i++;
				}
			} else {
				$arrayicon = $arraycheck;
			}
			$options = arg2array($_options['title']);
			if (isset($options['blink']) && $options['blink'] == 1) {
				$_data['blink'] = 1;
			}
			$image = $arrayicon[array_rand($arrayicon)];
			if (strpos($image,'.gif') !== false) {
				$path = dirname(__FILE__) . '/../../../../../data/divoompixoo/'.$image;
				$return=array('type' => 'displaydynamic', 'path' => $path);
			} else if (strpos($image,'.png') !== false || strpos($image,'.bmp') !== false) {
				$path = dirname(__FILE__) . '/../../../../../data/divoompixoo/'.$image;
				$return=array('type' => 'display', 'path' => $path);
			} else {
				$return = self::sendData($_eqLogic,'display', self::getImageData($arrayicon[array_rand($arrayicon)]));
			}
		}
		elseif ($logicalid == 'show_text') {
			$options = arg2array($_options['title']);
			if (!isset($options['color'])) {
				$options['color'] = '#0000ff';
			}
			if (!isset($options['speed'])) {
				$options['speed'] = 12;
			}
			if ($options['speed']>20) {
				$options['speed'] = 12;
			}
			$textArray=array();
			$messageArray = explode('||',$_options['message']);
			foreach($messageArray as $message) {
				$messageColor = explode('##',$message);
				if (count($messageColor) >1) {
					$textArray[$messageColor[0]] = '#'.trim($messageColor[1]);
				} else {
					$textArray[$messageColor[0]] = $options['color'];
				}
			}
			$_data['text'] = $textArray;
			$_data['speed'] = $options['speed'];
		}
		elseif ($logicalid == 'show_clock') {
			$options = arg2array($_options['title']);
			if (!isset($options['color'])) {
				$options['color'] = '#0000ff';
			}
			$_data['color'] = $options['color'];
			$_data['type'] = 'show_clock';
		}
		elseif ($logicalid == 'show_temp') {
			$options = arg2array($_options['title']);
			if (!isset($options['color'])) {
				$options['color'] = '#0000ff';
			}
			$_data['color'] = $options['color'];
			$_data['type'] = 'show_temp';
		}
		elseif ($logicalid == 'raw') {
			$options = arg2array($_options['title']);
			if (!isset($options['raw'])) {
				$options['raw'] = '#0000ff';
			}
			$_data['raw'] = $options['raw'];
		}
		elseif ($logicalid == 'luminosity') {
			$_data['slider'] = $_options['slider'];
		}
		elseif ($logicalid == 'temperature') {
			if ($_options['title'] == ''){
					$_options['title'] = '1';
			}
			if ($_options['message'] == ''){
					$_options['message'] = '25';
			}
			$_data['temperature'] = round($_options['message']);
			$_data['icon'] = $_options['title'];
		}
		elseif ($logicalid == 'effets') {
			if ($_options['message'] == ''){
					$_options['message'] = rand(0,16);
			}
			$_data['effectype'] = '3';
			$_data['visual'] = $_options['message'];
		}
		elseif ($logicalid == 'effetsmusic') {
			if ($_options['message'] == ''){
					$_options['message'] = rand(0,16);
			}
			$_data['effectype'] = '4';
			$_data['visual'] = $_options['message'];
		}
		elseif ($logicalid == 'favoris') {
			$_data['effectype'] = '5';
			$_data['visual'] = '0';
		}
		elseif ($logicalid == 'notifs') {
			if ($_options['message'] == ''){
					$_options['message'] = rand(0,16);
			}
			$_data['icon'] = $_options['message'];
		}
		elseif ($logicalid == 'showtime') {
			if ($_options['message'] == ''){
					$_options['message'] = rand(0,7);
			}
			if ($_options['title'] == ''){
						$_options['title'] = '#0000FF';
				}
			$_data['color'] = $_options['title'];
		  $_data['mode'] = $_options['message'];
		}
		elseif ($logicalid == 'showtimeseq') {
			$options = arg2array($_options['message']);
			if (!isset($options['mode'])) {
				$options['mode'] = rand(0,6);
			}
			if (!isset($options['clock'])) {
				$options['clock'] = 0;
			}
			if (!isset($options['temp'])) {
				$options['temp'] = 0;
			}
			if (!isset($options['weather'])) {
				$options['weather'] = 0;
			}
			if (!isset($options['date'])) {
				$options['date'] = 0;
			}
			if ($_options['title'] == ''){
						$_options['title'] = '#0000FF';
			}
			$_data['color'] = $_options['title'];
			$_data['mode'] = $options['mode'];
			$_data['clock'] = $options['clock'];
			$_data['weather'] = $options['weather'];
		  $_data['temp'] = $options['temp'];
		  $_data['date'] = $options['date'];
		}
		foreach ($return as $key => $value){
			$_data[$key]=$value;
		}
		$_eqLogic->setCache('previousDisplay', $_eqLogic->getCache('display', array()));
		$_eqLogic->setCache('display', $_data);
		return $_data;
	}

	public static function calculateInputValue($_eqLogic,$_datas) {
	}
}

?>
