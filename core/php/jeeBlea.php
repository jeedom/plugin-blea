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
require_once dirname(__FILE__) . "/../../../../core/php/core.inc.php";

if (!jeedom::apiAccess(init('apikey'), 'blea')) {
	echo 'Clef API non valide, vous n\'etes pas autorisé à effectuer cette action';
	die();
}

if (init('test') != '') {
	echo 'OK';
	die();
}
$result = json_decode(file_get_contents("php://input"), true);
if (!is_array($result)) {
	die();
}
if (isset($result['source'])){
	log::add('blea','debug','This is a message from antenna ' . $result['source']);
}
if (isset($result['learn_mode'])) {
	if ($result['learn_mode'] == 1) {
		config::save('include_mode', 1, 'blea');
		event::add('blea::includeState', array(
			'mode' => 'learn',
			'state' => 1)
		);
	} else {
		config::save('include_mode', 0, 'blea');
		event::add('blea::includeState', array(
			'mode' => 'learn',
			'state' => 0)
		);
	}
}

if (isset($result['started'])) {
	if ($result['started'] == 1) {
		log::add('blea','info','Antenna ' . $result['source'] . ' alive sending known devices');
		if ($result['source'] != 'local'){
			$remotes = blea_remote::all();
			foreach ($remotes as $remote){
				if ($remote->getRemoteName() == $result['source']){
					$remote->setConfiguration('lastupdate',date("Y-m-d H:i:s"));
					$remote->save();
					break;
				}
			}
		}
		usleep(500);
		blea::sendIdToDeamon();
	}
}
if (isset($result['heartbeat'])) {
	if ($result['heartbeat'] == 1) {
		log::add('blea','info','This is a heartbeat from antenna ' . $result['source']);
		if ($result['source'] != 'local'){
			$remotes = blea_remote::all();
			foreach ($remotes as $remote){
				if ($remote->getRemoteName() == $result['source']){
					$remote->setConfiguration('lastupdate',date("Y-m-d H:i:s"));
					$remote->save();
					break;
				}
			}
		}
	}
}

if (isset($result['devices'])) {
	foreach ($result['devices'] as $key => $datas) {
		if (!isset($datas['id'])) {
			continue;
		}
		if (isset($datas['source'])){
			log::add('blea','debug','This is a message from antenna ' . $datas['source']);
			if ($datas['source'] != 'local'){
				$remotes = blea_remote::all();
				foreach ($remotes as $remote){
					if ($remote->getRemoteName() == $datas['source']){
						$remote->setConfiguration('lastupdate',date("Y-m-d H:i:s"));
						$remote->save();
						break;
					}
				}
			}
		}
		$blea = blea::byLogicalId($datas['id'], 'blea');
		if (!is_object($blea)) {
			if ($datas['learn'] != 1) {
				continue;
			}
			log::add('blea','info','This is a learn from antenna ' . $datas['source']);
			$blea = blea::createFromDef($datas);
			if (!is_object($blea)) {
				log::add('blea', 'debug', __('Aucun équipement trouvé pour : ', __FILE__) . secureXSS($datas['id']));
				continue;
			}
			event::add('jeedom::alert', array(
				'level' => 'warning',
				'page' => 'blea',
				'message' => '',
			));
			$remotes = blea_remote::all();
			foreach ($remotes as $remote){
				if ($remote->getRemoteName() == $datas['source']){
					$blea->setConfiguration('antennareceive',$remote->getId());
					$blea->setConfiguration('antenna',$remote->getId());
					$blea->save();
					break;
				}
			}
			event::add('blea::includeDevice', $blea->getId());
		}
		if (!$blea->getIsEnable()) {
			continue;
		}
		if (isset($datas['specificconfiguration'])) {
			$blea->setConfiguration('specificconfiguration',$datas['specificconfiguration']);
			$blea->save();
		}
		if (isset($datas['rssi'])) {
			$rssicmd = $blea->getCmd(null, 'rssi' . $datas['source']);
			if (!is_object($rssicmd)) {
				$rssicmd = new bleaCmd();
				$rssicmd->setLogicalId('rssi' . $datas['source']);
				$rssicmd->setIsVisible(0);
				$rssicmd->setIsHistorized(1);
				$rssicmd->setName(__('Rssi '. $datas['source'], __FILE__));
				$rssicmd->setType('info');
				$rssicmd->setSubType('numeric');
				$rssicmd->setUnite('dbm');
				$rssicmd->setEqLogic_id($blea->getId());
				$rssicmd->save();
			}
			if ($rssicmd->getConfiguration('returnStateValue') == -200 || $rssicmd->getConfiguration('returnStateTime') == 2){
				$rssicmd->setConfiguration('returnStateValue','');
				$rssicmd->setConfiguration('returnStateTime','');
				$rssicmd->save();
			}
			$presentcmd = $blea->getCmd(null, 'present' . $datas['source']);
			if (!is_object($presentcmd)) {
				$presentcmd = new bleaCmd();
				$presentcmd->setLogicalId('present' . $datas['source']);
				$presentcmd->setIsVisible(0);
				$presentcmd->setIsHistorized(1);
				$presentcmd->setName(__('Present '. $datas['source'], __FILE__));
				$presentcmd->setType('info');
				$presentcmd->setSubType('binary');
				$presentcmd->setTemplate('dashboard','line');
				$presentcmd->setTemplate('mobile','line');
				$presentcmd->setEqLogic_id($blea->getId());
				$presentcmd->save();
			}
			if ($datas['rssi']=='same'){
				$oldrssi = $cmd->execCmd();
				$cmdremote->event($oldrssi);
				$presentcmd->event(1);
				die();
			}
			$cmdraw = $blea->getCmd(null, 'rawdata');
			if (!is_object($cmdraw)) {
				$cmdraw = new bleaCmd();
				$cmdraw->setLogicalId('rawdata');
				$cmdraw->setIsVisible(0);
				$cmdraw->setIsHistorized(0);
				$cmdraw->setName(__('Données brutes', __FILE__));
				$cmdraw->setType('info');
				$cmdraw->setSubType('string');
				$cmdraw->setEqLogic_id($blea->getId());
				$cmdraw->save();
			}
			$rssicmd->event($datas['rssi']);
			$presentcmd->event($datas['present']);
		}
		$remotelist =['rssilocal'];
		$remotes = blea_remote::all();
		foreach ($remotes as $remote){
			$name = $remote->getRemoteName();
			$remotelist[]='rssi' . $name;
		}
		$cmdrssitoremove=[];
		if ($blea->getConfiguration('specificclass',0) != 0) {
			$device= $blea->getConfiguration('device');
			require_once dirname(__FILE__) . '/../config/devices/'.$device.'/class/'.$device.'.class.php';
			$class= $device.'blea';
			$childrenclass = new $class();
			$datas = $childrenclass->calculateInputValue($blea,$datas);
		}
		foreach ($blea->getCmd('info') as $cmd) {
			$logicalId = $cmd->getLogicalId();
			if ($logicalId == '' || $logicalId == 'present') {
				continue;
			}
			if (substr($logicalId,0,4) == 'rssi'){
				if (!in_array($logicalId,$remotelist)){
					$cmdrssitoremove[]=$cmd;
				}
			}
			$path = explode('::', $logicalId);
			$value = $datas;
			foreach ($path as $key) {
				if (!isset($value[$key])) {
					continue (2);
				}
				$value = $value[$key];
			}
			if ($logicalId == 'rssi' && $datas['source'] != 'local') {
				continue;
			}
			$antenna = 'local';
			$antennaId = $blea->getConfiguration('antennareceive','local');
			if ($antennaId != 'local' && $antennaId != 'all'){
				$remote = blea_remote::byId($antennaId);
				$antenna = $remote->getRemoteName();
			}
			if ($logicalId != 'present' && $antennaId != 'all' && $antenna != $datas['source']){
				log::add('blea','debug','Ignoring this antenna (' . $datas['source'] . ' only allowed ' . $antenna .') must not trigger events except for presence and rssi : ' . $logicalId );
				continue;
			}
			if (!is_array($value)) {
				$cmd->event($value);
			}
			if ($logicalId == 'battery') {
				$blea->batteryStatus($value);
			}
		}
		foreach ($cmdrssitoremove as $cmdremove){
			$cmdremove->remove();
		}
		$blea->computePresence();
	}
}
