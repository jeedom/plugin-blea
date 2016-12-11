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
class blea extends eqLogic {
	/*     * ***********************Methode static*************************** */

	public static function createFromDef($_def) {
		event::add('jeedom::alert', array(
			'level' => 'warning',
			'page' => 'blea',
			'message' => __('Nouveau module detecté', __FILE__),
		));
		if (!isset($_def['id']) || !isset($_def['type'])) {
			log::add('blea', 'error', 'Information manquante pour ajouter l\'équipement : ' . print_r($_def, true));
			event::add('jeedom::alert', array(
				'level' => 'danger',
				'page' => 'blea',
				'message' => __('Information manquante pour ajouter l\'équipement. Inclusion impossible', __FILE__),
			));
			return false;
		}
		$device = self::devicesParameters($_def['type']);
		$blea = blea::byLogicalId($_def['id'], 'blea');
		if (!is_object($blea)) {
			$eqLogic = new blea();
			$eqLogic->setName('BLE ' . $_def['name'] . ' ' . $_def['id']);
		}
		$eqLogic->setLogicalId($_def['id']);
		$eqLogic->setEqType_name('blea');
		$eqLogic->setIsEnable(1);
		$eqLogic->setIsVisible(1);
		$eqLogic->setConfiguration('device', $_def['type']);
		$model = $eqLogic->getModelListParam();
		if (count($model) > 0) {
			$eqLogic->setConfiguration('iconModel', array_keys($model[0])[0]);
			if ($_def['type'] == 'niu') {
				$eqLogic->setConfiguration('iconModel', 'niu/niu_' . strtolower($_def['color']));
			}
		}
		$eqLogic->save();

		event::add('jeedom::alert', array(
			'level' => 'warning',
			'page' => 'blea',
			'message' => __('Module inclu avec succès', __FILE__),
		));
		return $eqLogic;
	}
	
	public static function cron15() {
		$remotes = blea_remote::all();
		foreach ($remotes as $remote) {
			$remote->getRemoteLog($remote->getId());
		}
	}
	
	public static function sendRemoteFiles($_remoteId) {
		blea::stopremote($_remoteId);
		$remoteObject = blea_remote::byId($_remoteId);
		$user=$remoteObject->getConfiguration('remoteUser');
		$script_path = dirname(__FILE__) . '/../../resources/';
		log::add('blea','info','Compression du dossier local');
		exec('tar -zcvf /tmp/folder-blea.tar.gz ' . $script_path);
		log::add('blea','info','Envoie du fichier  /tmp/folder-blea.tar.gz');
		$remoteObject->sendFiles('/tmp/folder-blea.tar.gz','folder-blea.tar.gz');
		log::add('blea','info','Décompression du dossier distant');
		$remoteObject->execCmd(['mkdir /home','mkdir /home/'.$user,'rm -R /home/'.$user.'/blead','mkdir /home/'.$user.'/blead','tar -zxf /home/'.$user.'/folder-blea.tar.gz -C /home/'.$user.'/blead','rm /home/'.$user.'/folder-blea.tar.gz']);
		log::add('blea','info','Suppression du zip local');
		exec('rm /tmp/folder-blea.tar.gz');
		blea::launchremote($_remoteId);
	}
	
	public static function getRemoteLog($_remoteId) {
		$remoteObject = blea_remote::byId($_remoteId);
		$name = $remoteObject->getRemoteName();
		$local = dirname(__FILE__) . '/../../../../log/blea_'.$name;
		log::add('blea','info','Suppression de la log');
		exec('rm '. $local);
		log::add('blea','info','Récupération de la log distante');
		$remoteObject->getFiles($local,'/tmp/blea');
		$remoteObject->execCmd(['cat /dev/null > /tmp/blea']);
	}
	
	public static function dependancyRemote($_remoteId) {
		blea::stopremote($_remoteId);
		$remoteObject = blea_remote::byId($_remoteId);
		$user=$remoteObject->getConfiguration('remoteUser');
		log::add('blea','info','Installation des dépendances');
		$remoteObject->execCmd(['/home/'.$user.'/blead/resources/install.sh']);
		blea::launchremote($_remoteId);
	}
	
	public static function launchremote($_remoteId) {
		blea::stopremote($_remoteId);
		$remoteObject = blea_remote::byId($_remoteId);
		$user=$remoteObject->getConfiguration('remoteUser');
		$device=$remoteObject->getConfiguration('remoteDevice');
		$script_path = '/home/'.$user.'/blead/resources/blead';
		$cmd = '/usr/bin/python ' . $script_path . '/blead.py';
		$cmd .= ' --loglevel debug';
		$cmd .= ' --device ' . $device;
		$cmd .= ' --socketport ' . config::byKey('socketport', 'blea');
		$cmd .= ' --sockethost ""';
		$cmd .= ' --callback ' . network::getNetworkAccess('internal') . '/plugins/blea/core/php/jeeBlea.php';
		$cmd .= ' --apikey ' . jeedom::getApiKey('blea');
		$cmd .= ' --daemonname "' . $remoteObject->getRemoteName() . '"';
		$cmd .= ' >> ' . '/tmp/blea' . ' 2>&1 &';
		log::add('blea','info','Lancement du démon distant ' . $cmd);
		$result = $remoteObject->execCmd([$cmd]);
		log::add('blea','info',$result);
		usleep(4000000);
		self::sendIdToDeamon();
		config::save('exclude_mode', 0, 'blea');
		config::save('include_mode', 0, 'blea');
	}
	
	public static function remotelearn($_remoteId,$_state) {
		$remoteObject = blea_remote::byId($_remoteId);
		$ip = $remoteObject->getConfiguration('remoteIp');
		if ($_state == '1'){
			$value = array('apikey' => jeedom::getApiKey('blea'), 'cmd' => 'learnin');
		} else {
			$value = array('apikey' => jeedom::getApiKey('blea'), 'cmd' => 'learnout');
		}
		$value = json_encode($value);
		$socket = socket_create(AF_INET, SOCK_STREAM, 0);
		socket_connect($socket, $ip, config::byKey('socketport', 'blea'));
		socket_write($socket, $value, strlen($value));
		socket_close($socket);
	}
	
	public static function stopremote($_remoteId) {
		log::add('blea','info','Arret du démon distant');
		$remoteObject = blea_remote::byId($_remoteId);
		$ip = $remoteObject->getConfiguration('remoteIp');
		$value = array('apikey' => jeedom::getApiKey('blea'), 'cmd' => 'stop');
		$value = json_encode($value);
		$socket = socket_create(AF_INET, SOCK_STREAM, 0);
		socket_connect($socket, $ip, config::byKey('socketport', 'blea'));
		socket_write($socket, $value, strlen($value));
		socket_close($socket);
	}
	
	public static function aliveremote($_remoteId) {
		log::add('blea','info','checking is alive');
		$remoteObject = blea_remote::byId($_remoteId);
		$ip = $remoteObject->getConfiguration('remoteIp');
		$socket = socket_create(AF_INET, SOCK_STREAM, 0);
		
		socket_connect($socket, $ip, config::byKey('socketport', 'blea'));
		$result = socket_read($socket,2000);
		if ($result === "") {
			
			log::add('blea','info','dead');
			return False;
		}
		else {
		log::add('blea','info','alive');
			return True;
		}
		socket_close($socket);
	}

	public static function devicesParameters($_device = '') {
		$return = array();
		foreach (ls(dirname(__FILE__) . '/../config/devices', '*') as $dir) {
			$path = dirname(__FILE__) . '/../config/devices/' . $dir;
			if (!is_dir($path)) {
				continue;
			}
			$files = ls($path, '*.json', false, array('files', 'quiet'));
			foreach ($files as $file) {
				try {
					$content = file_get_contents($path . '/' . $file);
					if (is_json($content)) {
						$return += json_decode($content, true);
					}
				} catch (Exception $e) {

				}
			}
		}
		if (isset($_device) && $_device != '') {
			if (isset($return[$_device])) {
				return $return[$_device];
			}
			return array();
		}
		return $return;
	}

	public static function deamon_info() {
		$return = array();
		$return['log'] = 'blea';
		$return['state'] = 'nok';
		$pid_file = '/tmp/blead.pid';
		if (file_exists($pid_file)) {
			if (@posix_getsid(trim(file_get_contents($pid_file)))) {
				$return['state'] = 'ok';
			} else {
				shell_exec('sudo rm -rf ' . $pid_file . ' 2>&1 > /dev/null;rm -rf ' . $pid_file . ' 2>&1 > /dev/null;');
			}
		}
		$return['launchable'] = 'ok';
		$port = jeedom::getBluetoothMapping(config::byKey('port', 'blea'));
		if ($port == '') {
			$return['launchable'] = 'nok';
			$return['launchable_message'] = __('Le port n\'est pas configuré', __FILE__);
		}
		return $return;
	}

	public static function dependancy_info() {
		$return = array();
		$return['log'] = 'blea_update';
		$return['progress_file'] = '/tmp/dependancy_blea_in_progress';
		if (exec('sudo pip list | grep -E "bluepy" | wc -l') < 1 || exec('which hcitool | wc -l') == 0) {
			$return['state'] = 'nok';
		} else {
			$return['state'] = 'ok';
		}
		return $return;
	}

	public static function dependancy_install() {
		log::remove('blea_update');
		$cmd = 'sudo /bin/bash ' . dirname(__FILE__) . '/../../resources/install.sh';
		$cmd .= ' >> ' . log::getPathToLog('blea_dependancy') . ' 2>&1 &';
		exec($cmd);
	}

	public static function deamon_start() {
		self::deamon_stop();
		$deamon_info = self::deamon_info();
		if ($deamon_info['launchable'] != 'ok') {
			throw new Exception(__('Veuillez vérifier la configuration', __FILE__));
		}
		$port = jeedom::getBluetoothMapping(config::byKey('port', 'blea'));
		$blea_path = realpath(dirname(__FILE__) . '/../../resources/blead');
		$cmd = 'sudo /usr/bin/python ' . $blea_path . '/blead.py';
		$cmd .= ' --loglevel ' . log::convertLogLevel(log::getLogLevel('blea'));
		$cmd .= ' --device ' . $port;
		$cmd .= ' --socketport ' . config::byKey('socketport', 'blea');
		$cmd .= ' --sockethost 127.0.0.1';
		$cmd .= ' --callback ' . network::getNetworkAccess('internal', 'proto:127.0.0.1:port:comp') . '/plugins/blea/core/php/jeeBlea.php';
		$cmd .= ' --apikey ' . jeedom::getApiKey('blea');
		$cmd .= ' --daemonname local';
		log::add('blea', 'info', 'Lancement démon blea : ' . $cmd);
		$result = exec($cmd . ' >> ' . log::getPathToLog('blea') . ' 2>&1 &');
		$i = 0;
		while ($i < 30) {
			$deamon_info = self::deamon_info();
			if ($deamon_info['state'] == 'ok') {
				break;
			}
			sleep(1);
			$i++;
		}
		if ($i >= 30) {
			log::add('blea', 'error', 'Impossible de lancer le démon blea, vérifiez la log', 'unableStartDeamon');
			return false;
		}
		message::removeAll('blea', 'unableStartDeamon');
		sleep(2);
		self::sendIdToDeamon();
		config::save('exclude_mode', 0, 'blea');
		config::save('include_mode', 0, 'blea');
		return true;
	}

	public static function sendIdToDeamon() {
		foreach (self::byType('blea') as $eqLogic) {
			$eqLogic->allowDevice();
			usleep(500);
		}
	}
	
	public static function changeLogLive($_level) {
		$value = array('apikey' => jeedom::getApiKey('blea'), 'cmd' => $_level);
		$value = json_encode($value);
		$socket = socket_create(AF_INET, SOCK_STREAM, 0);
		socket_connect($socket, '127.0.0.1', config::byKey('socketport', 'blea'));
		socket_write($socket, $value, strlen($value));
		socket_close($socket);
	}

	public static function deamon_stop() {
		$pid_file = '/tmp/blead.pid';
		if (file_exists($pid_file)) {
			$pid = intval(trim(file_get_contents($pid_file)));
			system::kill($pid);
		}
		system::kill('blead.py');
		system::fuserk(config::byKey('socketport', 'blea'));
		sleep(1);
	}

	public static function excludedDevice($_logical_id = null) {
		$eqLogic = eqlogic::byLogicalId($_logical_id, 'blea');
		if (is_object($eqLogic)) {
			event::add('jeedom::alert', array(
				'level' => 'warning',
				'page' => 'blea',
				'message' => __('Le module ', __FILE__) . $eqLogic->getHumanName() . __(' vient d\'être exclu', __FILE__),
			));
			sleep(3);
			if (config::byKey('autoRemoveExcludeDevice', 'blea') == 1) {
				$eqLogic->remove();
				event::add('blea::includeDevice', '');
			}
			sleep(3);
			event::add('jeedom::alert', array(
				'level' => 'warning',
				'page' => 'blea',
				'message' => '',
			));
			return;
		}
		sleep(2);
		event::add('jeedom::alert', array(
			'level' => 'warning',
			'page' => 'blea',
			'message' => '',
		));
		return;
	}

	public static function changeIncludeState($_state, $_mode) {
		if ($_mode == 1) {
			if ($_state == 1) {
				$value = json_encode(array('apikey' => jeedom::getApiKey('blea'), 'cmd' => 'learnin'));
			} else {
				$value = json_encode(array('apikey' => jeedom::getApiKey('blea'), 'cmd' => 'learnout'));
			}
		} else {
			if ($_state == 1) {
				$value = json_encode(array('apikey' => jeedom::getApiKey('blea'), 'cmd' => 'excludein'));
			} else {
				$value = json_encode(array('apikey' => jeedom::getApiKey('blea'), 'cmd' => 'excludeout'));
			}
		}
		if (config::byKey('port', 'blea', 'none') != 'none') {
			$socket = socket_create(AF_INET, SOCK_STREAM, 0);
			socket_connect($socket, '127.0.0.1', config::byKey('socketport', 'blea'));
			socket_write($socket, $value, strlen($value));
			socket_close($socket);
		}
	}
	public static function getTintedColor($hex, $lum) {
		$initColor = $hex;
		$hex = str_replace('#','',$hex);
		$lum = -((100-$lum)/100);
		if ($lum==0){
			return $initColor;
		}
		log::add('blea','debug',$hex . ' ' . $lum);
		$rgb = "#";
		foreach (range(0,2) as $i) {
			$c = intval(substr($hex,$i*2,2), 16);
			$c = strval(round(min(max(0, $c + ($c * $lum)), 255)));
			
			$rgb = $rgb . str_pad(dechex($c),2,'0',STR_PAD_LEFT);
		}
			return $rgb;
	}

/*     * *********************Methode d'instance************************* */
	public function getModelListParam($_conf = '') {
		if ($_conf == '') {
			$_conf = $this->getConfiguration('device');
		}
		$modelList = array();
		$param = false;
		$files = array();
		foreach (ls(dirname(__FILE__) . '/../config/devices', '*') as $dir) {
			if (!is_dir(dirname(__FILE__) . '/../config/devices/' . $dir)) {
				continue;
			}
			$files[$dir] = ls(dirname(__FILE__) . '/../config/devices/' . $dir, $_conf . '_*.jpg', false, array('files', 'quiet'));
			if (file_exists(dirname(__FILE__) . '/../config/devices/' . $dir . $_conf . '.jpg')) {
				$selected = 0;
				if ($dir . $_conf == $this->getConfiguration('iconModel')) {
					$selected = 1;
				}
				$modelList[$dir . $_conf] = array(
					'value' => __('Défaut', __FILE__),
					'selected' => $selected,
				);
			}
			if (count($files[$dir]) == 0) {
				unset($files[$dir]);
			}
		}
		$replace = array(
			$_conf => '',
			'.jpg' => '',
			'_' => ' ',
		);
		foreach ($files as $dir => $images) {
			foreach ($images as $imgname) {
				$selected = 0;
				if ($dir . str_replace('.jpg', '', $imgname) == $this->getConfiguration('iconModel')) {
					$selected = 1;
				}
				$modelList[$dir . str_replace('.jpg', '', $imgname)] = array(
					'value' => ucfirst(trim(str_replace(array_keys($replace), $replace, $imgname))),
					'selected' => $selected,
				);
			}
		}
		$needsrefresh = false;
		if ($this->getConfiguration('needsrefresh',0) != 0) {
			$needsrefresh = true;
		}
		return [$modelList, $needsrefresh];
	}

	public function postSave() {
		if ($this->getConfiguration('applyDevice') != $this->getConfiguration('device')) {
			$this->applyModuleConfiguration();
		} else {
			$this->allowDevice();
		}
	}

	public function preRemove() {
		$this->disallowDevice();
	}

	public function allowDevice() {
		$value = array('apikey' => jeedom::getApiKey('blea'), 'cmd' => 'add');
		if ($this->getLogicalId() != '') {
			$value['device'] = array(
				'id' => $this->getLogicalId(),
				'delay' => $this->getConfiguration('delay',0),
				'needsrefresh' => $this->getConfiguration('needsrefresh',0),
				'name' => $this->getConfiguration('name','0'),
			);
			$value = json_encode($value);
			if (config::byKey('port', 'blea', 'none') != 'none') {
				$socket = socket_create(AF_INET, SOCK_STREAM, 0);
				socket_connect($socket, '127.0.0.1', config::byKey('socketport', 'blea'));
				socket_write($socket, $value, strlen($value));
				socket_close($socket);
			}
			$remotes = blea_remote::all();
			foreach ($remotes as $remote) {
				$ip = $remote->getConfiguration('remoteIp');
				$socket = socket_create(AF_INET, SOCK_STREAM, 0);
				socket_connect($socket, $ip, config::byKey('socketport', 'blea'));
				socket_write($socket, $value, strlen($value));
				socket_close($socket);
			}
		}
	}

	public function disallowDevice() {
		if ($this->getLogicalId() == '') {
			return;
		}
		$value = json_encode(array('apikey' => jeedom::getApiKey('blea'), 'cmd' => 'remove', 'device' => array('id' => $this->getLogicalId())));
		if (config::byKey('port', 'blea', 'none') != 'none') {
			$socket = socket_create(AF_INET, SOCK_STREAM, 0);
			socket_connect($socket, '127.0.0.1', config::byKey('socketport', 'blea'));
			socket_write($socket, $value, strlen($value));
			socket_close($socket);
		}
		$remotes = blea_remote::all();
		foreach ($remotes as $remote) {
			$ip = $remote->getConfiguration('remoteIp');
			$socket = socket_create(AF_INET, SOCK_STREAM, 0);
			socket_connect($socket, $ip, config::byKey('socketport', 'blea'));
			socket_write($socket, $value, strlen($value));
			socket_close($socket);
		}
	}

	public function applyModuleConfiguration() {
		$this->setConfiguration('applyDevice', $this->getConfiguration('device'));
		$this->save();
		if ($this->getConfiguration('device') == '') {
			return true;
		}
		$device = self::devicesParameters($this->getConfiguration('device'));
		if (!is_array($device)) {
			return true;
		}
		event::add('jeedom::alert', array(
			'level' => 'warning',
			'page' => 'blea',
			'message' => __('Périphérique reconnu, intégration en cours', __FILE__),
		));
		$this->setConfiguration('needsrefresh', 0);
		$this->setConfiguration('name', '');
		$this->setConfiguration('hasspecificmodal', '');
		if (isset($device['configuration'])) {
			foreach ($device['configuration'] as $key => $value) {
				$this->setConfiguration($key, $value);
			}
		}
		if (isset($device['category'])) {
			foreach ($device['category'] as $key => $value) {
				$this->setCategory($key, $value);
			}
		}
		$cmd_order = 0;
		$link_cmds = array();
		$link_actions = array();
		event::add('jeedom::alert', array(
			'level' => 'warning',
			'page' => 'blea',
			'message' => __('Création des commandes', __FILE__),
		));

		$ids = array();
		$arrayToRemove = [];
		if (isset($device['commands'])) {
			foreach ($this->getCmd() as $eqLogic_cmd) {
				$exists = 0;
				foreach ($device['commands'] as $command) {
					if ($command['logicalId'] == $eqLogic_cmd->getLogicalId()) {
						$exists++;
					}
				}
				if ($exists < 1) {
					$arrayToRemove[] = $eqLogic_cmd;
				}
			}
			foreach ($arrayToRemove as $cmdToRemove) {
				try {
					$cmdToRemove->remove();
				} catch (Exception $e) {

				}
			}
			foreach ($device['commands'] as $command) {
				$cmd = null;
				foreach ($this->getCmd() as $liste_cmd) {
					if ((isset($command['logicalId']) && $liste_cmd->getLogicalId() == $command['logicalId'])
						|| (isset($command['name']) && $liste_cmd->getName() == $command['name'])) {
						$cmd = $liste_cmd;
						break;
					}
				}
				try {
					if ($cmd == null || !is_object($cmd)) {
						$cmd = new bleaCmd();
						$cmd->setOrder($cmd_order);
						$cmd->setEqLogic_id($this->getId());
					} else {
						$command['name'] = $cmd->getName();
						if (isset($command['display'])) {
							unset($command['display']);
						}
					}
					utils::a2o($cmd, $command);
					$cmd->setConfiguration('logicalId', $cmd->getLogicalId());
					$cmd->save();
					if (isset($command['value'])) {
						$link_cmds[$cmd->getId()] = $command['value'];
					}
					if (isset($command['configuration']) && isset($command['configuration']['updateCmdId'])) {
						$link_actions[$cmd->getId()] = $command['configuration']['updateCmdId'];
					}
					$cmd_order++;
				} catch (Exception $exc) {

				}
			}
		}

		if (count($link_cmds) > 0) {
			foreach ($this->getCmd() as $eqLogic_cmd) {
				foreach ($link_cmds as $cmd_id => $link_cmd) {
					if ($link_cmd == $eqLogic_cmd->getName()) {
						$cmd = cmd::byId($cmd_id);
						if (is_object($cmd)) {
							$cmd->setValue($eqLogic_cmd->getId());
							$cmd->save();
						}
					}
				}
			}
		}
		if (count($link_actions) > 0) {
			foreach ($this->getCmd() as $eqLogic_cmd) {
				foreach ($link_actions as $cmd_id => $link_action) {
					if ($link_action == $eqLogic_cmd->getName()) {
						$cmd = cmd::byId($cmd_id);
						if (is_object($cmd)) {
							$cmd->setConfiguration('updateCmdId', $eqLogic_cmd->getId());
							$cmd->save();
						}
					}
				}
			}
		}
		$this->save();
		if (isset($device['afterInclusionSend']) && $device['afterInclusionSend'] != '') {
			event::add('jeedom::alert', array(
				'level' => 'warning',
				'page' => 'blea',
				'message' => __('Envoi des commandes post-inclusion', __FILE__),
			));
			sleep(5);
			$sends = explode('&&', $device['afterInclusionSend']);
			foreach ($sends as $send) {
				foreach ($this->getCmd('action') as $cmd) {
					if (strtolower($cmd->getName()) == strtolower(trim($send))) {
						$cmd->execute();
					}
				}
				sleep(1);
			}

		}
		sleep(1);
		event::add('jeedom::alert', array(
			'level' => 'warning',
			'page' => 'blea',
			'message' => '',
		));
	}

}

class bleaCmd extends cmd {
	/*     * *************************Attributs****************************** */

	/*     * ***********************Methode static*************************** */

	/*     * *********************Methode d'instance************************* */

	public function execute($_options = null) {
		if ($this->getType() != 'action') {
			return;
		}
		$eqLogic = $this->getEqLogic();
		$values = explode(',', $this->getLogicalId());
		foreach ($values as $value) {
			$value = explode(':', $value);
			if (count($value) == 2) {
				switch ($this->getSubType()) {
					case 'slider':
						$data[trim($value[0])] = trim(str_replace('#slider#', $_options['slider'], $value[1]));
						break;
					case 'color':
						$data[trim($value[0])] = str_replace('#','',trim(str_replace('#color#', $_options['color'], $value[1])));
						break;
					default:
						$data[trim($value[0])] = trim($value[1]);
				}
			}
		}
		if (isset($data['secondary'])){
			$data['secondary'] = $eqLogic->getCmd('info',$data['secondary'])->execCmd();
		}
		$data['device'] = array(
				'id' => $eqLogic->getLogicalId(),
				'delay' => $eqLogic->getConfiguration('delay',0),
				'needsrefresh' => $eqLogic->getConfiguration('needsrefresh',0),
				'name' => $eqLogic->getConfiguration('name','0'),
		);
		if (count($data) == 0) {
			return;
		}
		if ($this->getLogicalId() == 'refresh'){
			$data['name'] = $eqLogic->getConfiguration('name','0');
			$value = json_encode(array('apikey' => jeedom::getApiKey('blea'), 'cmd' => 'refresh', 'device' => array('id' => $eqLogic->getLogicalId()), 'command' => $data));
		} else {
			$value = json_encode(array('apikey' => jeedom::getApiKey('blea'), 'cmd' => 'action', 'device' => array('id' => $eqLogic->getLogicalId()), 'command' => $data));
		}
		$sender = $eqLogic->getConfiguration('antenna','local');
		if ($sender == 'local' || $sender == 'all') {
			log::add('blea','info','Envoi depuis local');
			$socket = socket_create(AF_INET, SOCK_STREAM, 0);
			socket_connect($socket, '127.0.0.1', config::byKey('socketport', 'blea'));
			socket_write($socket, $value, strlen($value));
			socket_close($socket);
			if ($sender == 'all') {
				$remotes = blea_remote::all();
				foreach ($remotes as $remote) {
					log::add('blea','info','Envoi depuis ' . $remote->getRemoteName());
					$ip = $remote->getConfiguration('remoteIp');
					$socket = socket_create(AF_INET, SOCK_STREAM, 0);
					socket_connect($socket, $ip, config::byKey('socketport', 'blea'));
					socket_write($socket, $value, strlen($value));
					socket_close($socket);
				}
			}
		} else {
			$remote = blea_remote::byId($sender);
			log::add('blea','info','Envoi depuis ' . $remote->getRemoteName());
			$ip = $remote->getConfiguration('remoteIp');
			$socket = socket_create(AF_INET, SOCK_STREAM, 0);
			socket_connect($socket, $ip, config::byKey('socketport', 'blea'));
			socket_write($socket, $value, strlen($value));
			socket_close($socket);
		}
	}
}

class blea_remote {
	/*     * *************************Attributs****************************** */
	private $id;
	private $remoteName;
	private $configuration;

	/*     * ***********************Methode static*************************** */

	public static function byId($_id) {
		$values = array(
			'id' => $_id,
		);
		$sql = 'SELECT ' . DB::buildField(__CLASS__) . '
		FROM blea_remote
		WHERE id=:id';
		return DB::Prepare($sql, $values, DB::FETCH_TYPE_ROW, PDO::FETCH_CLASS, __CLASS__);
	}

	public static function all() {
		$sql = 'SELECT ' . DB::buildField(__CLASS__) . '
		FROM blea_remote';
		return DB::Prepare($sql, array(), DB::FETCH_TYPE_ALL, PDO::FETCH_CLASS, __CLASS__);
	}

	/*     * *********************Methode d'instance************************* */

	public function save() {
		return DB::save($this);
	}

	public function remove() {
		return DB::remove($this);
	}

	public function execCmd($_cmd) {
		$ip = $this->getConfiguration('remoteIp');
		$port = $this->getConfiguration('remotePort');
		$user = $this->getConfiguration('remoteUser');
		$pass = $this->getConfiguration('remotePassword');
		if (!$connection = ssh2_connect($ip, $port)) {
			log::add('blea', 'error', 'connexion SSH KO');
		} else {
			if (!ssh2_auth_password($connection, $user, $pass)) {
				log::add('blea', 'error', 'Authentification SSH KO');
			} else {
				foreach ($_cmd as $cmd){
					log::add('blea', 'info', 'Commande par SSH (' . $cmd . ') sur ' . $ip);
					$execmd = "echo '" . $pass . "' | sudo -S " . $cmd;
					$result = ssh2_exec($connection, $execmd);
				}
				$closesession = ssh2_exec($connection, 'exit');
				stream_set_blocking($closesession, true);
				stream_get_contents($closesession);
				return $result;
			}
		}
	}

	public function sendFiles($_local, $_target) {
		$ip = $this->getConfiguration('remoteIp');
		$port = $this->getConfiguration('remotePort');
		$user = $this->getConfiguration('remoteUser');
		$pass = $this->getConfiguration('remotePassword');
		if (!$connection = ssh2_connect($ip, $port)) {
			log::add('blea', 'error', 'connexion SSH KO');
		} else {
			if (!ssh2_auth_password($connection, $user, $pass)) {
				log::add('blea', 'error', 'Authentification SSH KO');
			} else {
				log::add('blea', 'info', 'Envoie de fichier sur ' . $ip);
				$result = ssh2_scp_send($connection, $_local, '/home/' . $user . '/' . $_target, 0777);
				$closesession = ssh2_exec($connection, 'exit');
				stream_set_blocking($closesession, true);
				stream_get_contents($closesession);
			}
		}
	}
	
	public function getFiles($_local, $_target) {
		$ip = $this->getConfiguration('remoteIp');
		$port = $this->getConfiguration('remotePort');
		$user = $this->getConfiguration('remoteUser');
		$pass = $this->getConfiguration('remotePassword');
		if (!$connection = ssh2_connect($ip, $port)) {
			log::add('blea', 'error', 'connexion SSH KO');
		} else {
			if (!ssh2_auth_password($connection, $user, $pass)) {
				log::add('blea', 'error', 'Authentification SSH KO');
			} else {
				log::add('blea', 'info', 'Envoie de fichier sur ' . $ip);
				$result = ssh2_scp_recv($connection, $_target, $_local);
				$closesession = ssh2_exec($connection, 'exit');
				stream_set_blocking($closesession, true);
				stream_get_contents($closesession);
			}
		}
	}

	/*     * **********************Getteur Setteur*************************** */

	public function getId() {
		return $this->id;
	}

	public function setId($id) {
		$this->id = $id;
		return $this;
	}

	public function getRemoteName() {
		return $this->remoteName;
	}

	public function setRemoteName($name) {
		$this->remoteName = $name;
		return $this;
	}

	public function getConfiguration($_key = '', $_default = '') {
		return utils::getJsonAttr($this->configuration, $_key, $_default);
	}

	public function setConfiguration($_key, $_value) {
		$this->configuration = utils::setJsonAttr($this->configuration, $_key, $_value);
		return $this;
	}

}
