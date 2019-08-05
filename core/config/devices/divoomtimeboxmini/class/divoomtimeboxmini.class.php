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

class divoomtimeboxminiblea extends blea {
	public static function text2array($_text, $_color = 'FFFFFF', $_displaySize = array(8, 8)) {
		$image = imagecreatetruecolor($_displaySize[0] + 1, $_displaySize[1] + 1);
		$rgbcolor = hex2rgb($_color);
		imagefill($image, 0, 0, 0x000000);
		imagestring($image, 1, 0, 0, $_text, 0xFFFFFF);
		$return = array();
		for ($x = 0; $x < imagesy($image); $x++) {
			for ($y = 0; $y < imagesx($image); $y++) {
				if (imagecolorat($image, $y, $x) != 0) {
					$return[$x][$y] = array($rgbcolor[0], $rgbcolor[1], $rgbcolor[2]);
				} else {
					$return[$x][$y] = array(0, 0, 0);
				}
			}
		}
		$column_black = true;
		foreach ($return as $x => $line) {
			if ($line[0][0] != 0 || $line[0][0] != 0 || $line[0][0] != 0) {
				$column_black = false;
				break;
			}
		}
		foreach ($return as $x => &$line) {
			if ($column_black) {
				array_shift($line);
			} else {
				array_pop($line);
			}
		}
		array_pop($return);
		return $return;
	}

	public static function number2line($_number, $_line = 1) {
		$return = array();
		$colors = array(
			1000 => '#FF0000',
			100 => '#FFFF00',
			10 => '#00FF00',
			1 => '#FFFFFF',
		);
		$start = ($_line - 1) * 8 + 1;
		$i = 0;
		for ($j = 0; $j < 8; $j++) {
			$return[$start + $j] = array(0, 0, 0);
		}
		foreach ($colors as $key => $color) {
			if (($_number / $key) >= 1) {
				for ($j = 1; $j <= ($_number / $key); $j++) {
					$return[$start + $i] = hex2rgb($color);
					if ($i == 7) {
						break (2);
					}
					$i++;
				}
				$_number = $_number - (floor($_number / $key) * $key);
			}
		}
		return $return;
	}

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
		$divoomtimeboxmini = blea::byId($_id);
		$data = array();
		foreach ($_data as $pixel => $color) {
			$data[$pixel] = hex2rgb($color);
		}

		$cmd = $divoomtimeboxmini->getCmd('action','name:divoomtimeboxmini,classlogical:loadimage,type:display,value:calcul');
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
		$file = dirname(__FILE__) . '/../../../../../data/collection_divoomtimeboxmini.json';
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
			log::add('blea','error','prout');
			$file = dirname(__FILE__) . '/../../../../../data/divoomtimeboxmini/'.$_oriname;
			$extension = pathinfo($file, PATHINFO_EXTENSION);
			$new = dirname(__FILE__) . '/../../../../../data/divoomtimeboxmini/'.$_newname.'.'.$extension;
			rename($file,$new);
		} else {
			$file = dirname(__FILE__) . '/../../../../../data/collection_divoomtimeboxmini.json';
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
		divoomtimeboxminiblea::refreshTitles();
		return;
	}

	public static function getImageCode($_name) {
		$file = dirname(__FILE__) . '/../../../../../data/collection_divoomtimeboxmini.json';
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
			$file = dirname(__FILE__) . '/../../../../../data/divoomtimeboxmini/'.$_name;
			unlink($file);
		} else {
			$file = dirname(__FILE__) . '/../../../../../data/collection_divoomtimeboxmini.json';
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
		divoomtimeboxminiblea::refreshTitles();
		return;
	}

	public static function listMemory() {
		$file = dirname(__FILE__) . '/../../../../../data/collection_divoomtimeboxmini.json';
		$dataMemory = array();
		if (file_exists($file)) {
			$dataMemory = json_decode(file_get_contents($file), true);
		}
		$list = '';
		foreach ($dataMemory as $name => $data) {
			$list .= '<option value="' . strtolower($name) . '">' . ucfirst($name) . '</option>';
		}
		$count =0;
		$dir = dirname(__FILE__) . '/../../../../../data/divoomtimeboxmini';
		foreach (ls($dir, '*') as $file) {
			$count+=1;
		}
		return array($list,$count);
	}

	public static function getImageData($_name) {
		$file = dirname(__FILE__) . '/../../../../../data/collection_divoomtimeboxmini.json';
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
			divoomtimeboxminiblea::sendDataRealTime($_data, $_id);
		} catch (Exception $e) {
		}
		sleep(5);
		$directory = dirname(__FILE__) . '/../../../../../data/';
		if (!is_dir($directory)) {
			mkdir($directory);
		}
		$file = dirname(__FILE__) . '/../../../../../data/collection_divoomtimeboxmini.json';
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
		divoomtimeboxminiblea::refreshTitles();
	}

	public static function refreshTitles() {
		$file = dirname(__FILE__) . '/../../../../../data/collection_divoomtimeboxmini.json';
		$dataMemory = array();
		if (file_exists($file)) {
			$dataMemory = json_decode(file_get_contents($file), true);
		}
		ksort($dataMemory);
		$array = array();
		foreach ($dataMemory as $name => $data) {
			$array[] = $name;
		}
		$dir = dirname(__FILE__) . '/../../../../../data/divoomtimeboxmini';
		foreach (ls($dir, '*') as $file) {
			$array[] = $file;
		}
		foreach (blea::all() as $blea) {
			if ($blea->getConfiguration('device') == 'divoomtimeboxmini'){
				$cmd = $blea->getCmd('action', 'name:divoomtimeboxmini,classlogical:loadimage,type:display,value:calcul');
				$cmd->setDisplay('title_possibility_list', json_encode($array));
				$cmd->save();
				$blea->refreshWidget();
			}
		}
	}

	public static function cronDispatcher($_params) {
		$blea = blea::byId($_params['divoomtimeboxmini_id']);
		$cmd = $blea->getCmd('action','name:divoomtimeboxmini,classlogical:sendraw,handle:0x2a,type:display,value:calcul');
		if (is_object($cmd)){
			$cmd->execute(array('message' => $blea->getCache('previousDisplay')));
		}
	}

	public static function postSaveChild($_eqLogic) {
		divoomtimeboxminiblea::refreshTitles($_eqLogic);
	}

	public static function sendData( $_eqLogic,$_type, $_data, $_priority = 100, $_timeout = null) {
		$cron = cron::byClassAndFunction('divoomtimeboxminiblea', 'displayTimeout');
		if (is_object($cron)) {
			$cron->remove(false);
		}
		if ($_priority == -1) {
			$_eqLogic->setCache('priority', 0);
			$_priority = 0;
		}
		if ($_type == 'display') {
			if ($_eqLogic->getCache('priority', 0) > $_priority) {
				return;
			}
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
			$_eqLogic->setCache('priority', $_priority);
			if ($_data != $_eqLogic->getCache('display', array())) {
				if ($_eqLogic->getCache('previousDisplay', array()) != $_eqLogic->getCache('display', array())) {
					$_eqLogic->setCache('previousDisplay', $_eqLogic->getCache('display', array()));
				}
				$_eqLogic->setCache('display', $_data);
			}
			if ($_timeout !== null) {
				if ($_timeout < 2) {
					$_timeout = 2;
				}
				$cron = new cron();
				$cron->setClass('blea');
				$cron->setFunction('childrenCronDispatcher');
				$cron->setOption(array('divoomtimeboxmini_id' => intval($_eqLogic->getId()),'childclass' => 'divoomtimeboxmini', 'childfunction' => 'displayTimeout'));
				$cron->setLastRun(date('Y-m-d H:i:s'));
				$cron->setOnce(1);
				$cron->setSchedule(cron::convertDateToCron(strtotime("now") + $_timeout * 60));
				$cron->save();
			}
		}
		if ($_type == 'color') {
			$arraycolor = array();
			$i = 1;
			while ($i<122){
				$arraycolor[$i] = $_data;
				$i++;
			}
			if ($arraycolor != $_eqLogic->getCache('display', array())) {
				if ($_eqLogic->getCache('previousDisplay', array()) != $_eqLogic->getCache('display', array())) {
					$_eqLogic->setCache('previousDisplay', $_eqLogic->getCache('display', array()));
				}
				$_eqLogic->setCache('display', $arraycolor);
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
		return $_eqLogic->postToHtml($_version, template_replace($replace, getTemplate('core', $version, 'divoomtimeboxmini', 'blea')));
	}

	public static function calculateOutputValue($_eqLogic,$_data,$_options=null) {
		$return =array();
		$logicalid = $_data['classlogical'];
		if (in_array($logicalid,array('sendcolor','sendcolorBlink'))) {
			$return = self::sendData($_eqLogic,'color', hex2rgb($_options['color']));
		}
		elseif ($logicalid == 'blackscreen') {
			$return = self::sendData($_eqLogic,'color', hex2rgb('#000000'));
		}
		elseif ($logicalid == 'loadimage') {
			$options = arg2array($_options['message']);
			if (!isset($options['priority'])) {
				$options['priority'] = 100;
			}
			if (!isset($options['timeout'])) {
				$options['timeout'] = null;
			}
			if (isset($options['blink']) && $options['blink'] == 1) {
				$_data['blink'] = 1;
			}
			if (is_array($_options['title'])) {
				$return=array('type' => 'display', 'data' => $_options['title']);
			}
			else if (strpos($_options['title'],'.gif') !== false) {
				$path = dirname(__FILE__) . '/../../../../../data/divoomtimeboxmini/'.$_options['title'];
				$return=array('type' => 'displaydynamic', 'path' => $path);
			} else if (strpos($_options['title'],'.png') !== false || strpos($_options['title'],'.bmp') !== false) {
				$path = dirname(__FILE__) . '/../../../../../data/divoomtimeboxmini/'.$_options['title'];
				$return=array('type' => 'display', 'path' => $path);
			} else {
				$return = self::sendData($_eqLogic,'display', self::getImageData($_options['title']), $options['priority'], $options['timeout']);
			}
		}
		elseif ($logicalid == 'lastimage') {
			$return = self::sendData($_eqLogic,'display', $_eqLogic->getCache('previousDisplay'), -1);
		}
		elseif ($logicalid == 'sendrandom') {
			$arrayicon = array();
			$arraycheck = array();
			$file = dirname(__FILE__) . '/../../../../../data/collection_divoomtimeboxmini.json';
			$dataMemory = array();
			if (file_exists($file)) {
				$dataMemory = json_decode(file_get_contents($file), true);
			}
			foreach ($dataMemory as $name => $data) {
				$arraycheck[] = $name;
			}
			$dir = dirname(__FILE__) . '/../../../../../data/divoomtimeboxmini';
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
			if (!isset($options['priority'])) {
				$options['priority'] = 100;
			}
			if (!isset($options['timeout'])) {
				$options['timeout'] = null;
			}
			if (isset($options['blink']) && $options['blink'] == 1) {
				$_data['blink'] = 1;
			}
			$image = $arrayicon[array_rand($arrayicon)];
			if (strpos($image,'.gif') !== false) {
				$path = dirname(__FILE__) . '/../../../../../data/divoomtimeboxmini/'.$image;
				$return=array('type' => 'displaydynamic', 'path' => $path);
			} else if (strpos($image,'.png') !== false || strpos($image,'.bmp') !== false) {
				$path = dirname(__FILE__) . '/../../../../../data/divoomtimeboxmini/'.$image;
				$return=array('type' => 'display', 'path' => $path);
			} else {
				$return = self::sendData($_eqLogic,'display', self::getImageData($arrayicon[array_rand($arrayicon)]), $options['priority'], $options['timeout']);
			}
		}
		elseif ($logicalid == 'resetpriority') {
			$_eqLogic->setCache('priority', 0);
			return;
		}
		elseif ($logicalid == 'show_text') {
			$options = arg2array($_options['title']);
			if (!isset($options['color'])) {
				$options['color'] = '#0000ff';
			}
			if (!isset($options['speed'])) {
				$options['speed'] = 15;
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
		foreach ($return as $key => $value){
			$_data[$key]=$value;
		}

		return $_data;
	}

	public static function calculateInputValue($_eqLogic,$_datas) {
	}
}

?>
