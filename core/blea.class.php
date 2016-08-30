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
			$eqLogic->setName('BLE ' . $_def['type'] . ' ' . $_def['id']);
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
		$return['log'] = 'dotti_update';
		$return['progress_file'] = '/tmp/dependancy_blea_in_progress';
		if (exec('which hcitool | wc -l') != 0) {
			$return['state'] = 'ok';
		} else {
			$return['state'] = 'nok';
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
		$cmd .= ' --loglevel=' . log::convertLogLevel(log::getLogLevel('blea'));
		$cmd .= ' --device=' . $port;
		$cmd .= ' --socketport=' . config::byKey('socketport', 'blea');
		$cmd .= ' --sockethost=127.0.0.1';
		$cmd .= ' --callback=' . network::getNetworkAccess('internal', 'proto:127.0.0.1:port:comp') . '/plugins/blea/core/php/jeeBlea.php';
		$cmd .= ' --apikey=' . config::byKey('api');
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
				$value = json_encode(array('apikey' => config::byKey('api'), 'cmd' => 'learnin'));
			} else {
				$value = json_encode(array('apikey' => config::byKey('api'), 'cmd' => 'learnout'));
			}
		} else {
			if ($_state == 1) {
				$value = json_encode(array('apikey' => config::byKey('api'), 'cmd' => 'excludein'));
			} else {
				$value = json_encode(array('apikey' => config::byKey('api'), 'cmd' => 'excludeout'));
			}
		}
		if (config::byKey('port', 'blea', 'none') != 'none') {
			$socket = socket_create(AF_INET, SOCK_STREAM, 0);
			socket_connect($socket, '127.0.0.1', config::byKey('socketport', 'blea'));
			socket_write($socket, $value, strlen($value));
			socket_close($socket);
		}

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
		$json = self::devicesParameters($_conf);
		if (isset($json['parameters'])) {
			$param = true;
		}
		return [$modelList, $param];
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
		$value = array('apikey' => config::byKey('api'), 'cmd' => 'add');
		if ($this->getLogicalId() != '') {
			$value['device'] = array(
				'id' => $this->getLogicalId(),
			);
			$value = json_encode($value);
			if (config::byKey('port', 'blea', 'none') != 'none') {
				$socket = socket_create(AF_INET, SOCK_STREAM, 0);
				socket_connect($socket, '127.0.0.1', config::byKey('socketport', 'blea'));
				socket_write($socket, $value, strlen($value));
				socket_close($socket);
			}
		}
	}

	public function disallowDevice() {
		if ($this->getLogicalId() == '') {
			return;
		}
		$value = json_encode(array('apikey' => config::byKey('api'), 'cmd' => 'remove', 'device' => array('id' => $this->getLogicalId())));
		if (config::byKey('port', 'blea', 'none') != 'none') {
			$socket = socket_create(AF_INET, SOCK_STREAM, 0);
			socket_connect($socket, '127.0.0.1', config::byKey('socketport', 'blea'));
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

	/*     * **********************Getteur Setteur*************************** */

	public function getId() {
		return $this->id;
	}

	public function setId($id) {
		$this->id = $id;
	}

	public function getName() {
		return $this->remoteName;
	}

	public function setName($name) {
		$this->remoteName = $name;
	}

	public function getConfiguration($_key = '', $_default = '') {
		return utils::getJsonAttr($this->configuration, $_key, $_default);
	}

	public function setConfiguration($_key, $_value) {
		$this->configuration = utils::setJsonAttr($this->configuration, $_key, $_value);
	}

}
