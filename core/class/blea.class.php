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
	public static $_widgetPossibility = array('custom' => true);
	public static $_version = '2.9';
	public static $_bluepy_version = '1.1.4';
	public static function createFromDef($_def) {
		event::add('jeedom::alert', array(
			'level' => 'warning',
			'page' => 'blea',
			'message' => __('Nouveau module detecté ' . $_def['type'], __FILE__),
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
		$eqLogic->setConfiguration('antenna', 'local');
		$eqLogic->setConfiguration('antennareceive','local');
		$eqLogic->setConfiguration('canbelocked',0);
		$eqLogic->setConfiguration('islocked',0);
		$eqLogic->setConfiguration('cancontrol',0);
		$eqLogic->setConfiguration('resetRssis',1);
		$eqLogic->setConfiguration('name','0');
		$eqLogic->setConfiguration('refreshlist',array());
		$eqLogic->setConfiguration('specificclass',0);
		$eqLogic->setConfiguration('needsrefresh',0);
		$eqLogic->setConfiguration('specificwidgets',0);
		$model = $eqLogic->getModelListParam();
		if (count($model) > 0) {
			$eqLogic->setConfiguration('iconModel', array_keys($model[0])[0]);
		}
		$eqLogic->save();

		event::add('jeedom::alert', array(
			'level' => 'warning',
			'page' => 'blea',
			'message' => __('Module inclu avec succès ' .$_def['name'].' ' . $_def['id'], __FILE__),
		));
		return $eqLogic;
	}

	public static function cron() {
		$remotes = blea_remote::getCacheRemotes('allremotes',array());
		$allEqlogic = eqLogic::byType('blea');
		foreach ($remotes as $remote) {
			$last = $remote->getCache('lastupdate','0');
			if (($last == '0' or time() - strtotime($last)>65)) {
				$auto = $remote->getConfiguration('remoteDaemonAuto','0');
				foreach ($allEqlogic as $eqLogic){
					$rssicmd = $eqLogic->getCmd(null, 'rssi' . $remote->getRemoteName());
					$presentcmd = $eqLogic->getCmd(null, 'present' . $remote->getRemoteName());
					$eqLogic->checkAndUpdateCmd($presentcmd, 0);
					$eqLogic->checkAndUpdateCmd($rssicmd, -200);
					$eqLogic->setCache('rssi' . $remote->getRemoteName(),-200);
					$eqLogic->computePresence();
				}
				if ($auto == 1){
					log::add('blea','info','Restarting daemon on remote ' . $remote->getRemoteName());
					blea::launchremote($remote->getId());
				}
			}
		}
		$deamon_info = self::deamon_info();
		if ($deamon_info['state'] != 'ok'){
			foreach ($allEqlogic as $eqLogic){
				$rssicmd = $eqLogic->getCmd(null, 'rssilocal');
				$presentcmd = $eqLogic->getCmd(null, 'presentlocal');
				$eqLogic->checkAndUpdateCmd($presentcmd, 0);
				$eqLogic->checkAndUpdateCmd($rssicmd, -200);
				$eqLogic->setCache('rssilocal',-200);
				$eqLogic->computePresence();
			}
		}
	}

	public static function cron15() {
		$remotes = blea_remote::getCacheRemotes('allremotes',array());
		$availremote= array();
		foreach ($remotes as $remote) {
			self::getRemoteLog($remote->getId());
			$availremote[] = $remote->getRemoteName();
		}
		foreach (eqLogic::byType('blea') as $eqLogic){
			foreach ($eqLogic->getCmd('info') as $cmd) {
				$logicalId = $cmd->getLogicalId();
				if (substr($logicalId,0,4) == 'rssi'){
					$remotename= substr($logicalId,4);
					if ($remotename != 'local' && $remotename != 'local' && !(in_array($remotename,$availremote))){
						$cmd->remove();
					} else if ($remotename == 'local') {
						if (config::byKey('noLocal', 'blea', 0) == 1){
							$cmd->remove();
						}
					}
				} else if (substr($logicalId,0,7) == 'present' && $logicalId!= 'present') {
					$remotename= substr($logicalId,7);
					if ($remotename != 'local' && !(in_array($remotename,$availremote))){
						$cmd->remove();
					} else if ($remotename == 'local') {
						if (config::byKey('noLocal', 'blea', 0) == 1){
							$cmd->remove();
						}
					}
				}
			}
		}
	}

	public static function childrenCronDispatcher($_params) {
		$child = $_params['childclass'];
		require_once dirname(__FILE__) . '/../config/devices/'.$child.'/class/'.$child.'.class.php';
		$class= $child.'blea';
		$childrenclass = new $class();
		$childrenclass->cronDispatcher($_params);
	}

	public static function getMobileHealth() {
		$health='';
		$eqLogics = blea::byType('blea');
		foreach ($eqLogics as $eqLogic) {
			$opacity = ($eqLogic->getIsEnable()) ? '' : jeedom::getConfiguration('eqLogic:style:noactive');
			$alternateImg = $eqLogic->getConfiguration('iconModel');
			if (file_exists(dirname(__FILE__) . '/../../core/config/devices/' . $alternateImg . '.jpg')) {
				$img = '<img class="lazy" src="plugins/blea/core/config/devices/' . $alternateImg . '.jpg" height="30" width="30" style="' . $opacity . '"/>';
			} elseif (file_exists(dirname(__FILE__) . '/../../core/config/devices/' . $eqLogic->getConfiguration('device') . '.jpg')) {
				$img = '<img class="lazy" src="plugins/blea/core/config/devices/' . $eqLogic->getConfiguration('device') . '.jpg" height="30" width="30" style="' . $opacity . '"/>';
			} else {
				$img = '<img class="lazy" src="plugins/blea/doc/images/blea_icon.png" height="30" width="30" style="' . $opacity . '"/>';
			}
			$health .= '<tr><td>' . $img . '</td><td><span class="label label-success" style="font-size : 0.8em;">'. $eqLogic->getHumanName(true) . '</span></td>';
			$battery_status = '<span class="label label-success" style="font-size : 1em;">{{OK}}</span>';
			if ($eqLogic->getStatus('battery') < 20 && $eqLogic->getStatus('battery') != '') {
				$battery_status = '<span style="font-size : 1em;color:red">' . $eqLogic->getStatus('battery') . '%</span>';
			} elseif ($eqLogic->getStatus('battery') < 60 && $eqLogic->getStatus('battery') != '') {
				$battery_status = '<span style="font-size : 1em;color:orange">' . $eqLogic->getStatus('battery') . '%</span>';
			} elseif ($eqLogic->getStatus('battery') > 60 && $eqLogic->getStatus('battery') != '') {
				$battery_status = '<span style="font-size : 1em;color:green">' . $eqLogic->getStatus('battery') . '%</span>';
			} else {
				$battery_status = '<span style="font-size : 1em;color:grey" title="{{Secteur}}"><i class="fas fa-plug"></i></span>';
			}
			$health .= '<td>' . $battery_status . '</td>';
			$present = 0;
			$presentcmd = $eqLogic->getCmd('info', 'present');
			if (is_object($presentcmd)) {
				$present = $presentcmd->execCmd();
			}
			if ($present == 1){
				$present = '<span style="font-size : 1em;color:green" title="{{Présent}}"><i class="fas fa-check"></i></span>';
			} else {
				$present = '<span style="font-size : 1em;color:red" title="{{Absent}}"><i class="fas fa-times"></i></span>';
			}
			$health .= '<td>' . $present . '</td>';
			$health .= '<td><span style="font-size : 0.8em;cursor:default;">' . $eqLogic->getStatus('lastCommunication') . '</span></td>';
		}
		return $health;
	}

	public static function getMobileGraph() {
		$remotes = blea_remote::getCacheRemotes('allremotes',array());
		$eqLogics = array();
		$antennas = array();
		foreach ($remotes as $remote){
			$info = array();
			$name = $remote->getRemoteName();
			$info['x'] = $remote->getConfiguration('positionx',999);
			$info['y'] = $remote->getConfiguration('positiony',999);
			$last = $remote->getCache('lastupdate', '0');
			$info['dead'] = ( ($last == '0') or (time() - strtotime($last)>65) );
			$antennas[$name]=$info;
			$availremotename[]=$name;
		}
		$availremotename[]='local';
		if (config::byKey('noLocal', 'blea', 0) == 0){
			$infolocal=array();
			$infolocal['x'] = config::byKey('positionx', 'blea', 999);
			$infolocal['y'] = config::byKey('positiony', 'blea', 999);
			$antennas['local']=$infolocal;
		}
		foreach (eqLogic::byType('blea') as $eqLogic){
			$info =array();
			$object = $eqLogic->getObject();
			if (is_null($object)) {
				$object = 'Aucun';
			} else {
				$object = $object->getName();
			}
			$info['name'] = $eqLogic->getName().' ['.$object.']';
			$info['icon'] = $eqLogic->getConfiguration('iconModel');
			$info['rssi'] = array();
			foreach ($eqLogic->getCmd('info') as $cmd) {
				$logicalId = $cmd->getLogicalId();
				if (substr($logicalId,0,4) == 'rssi'){
					$remotename= substr($logicalId,4);
					$remoterssi = $cmd->execCmd();
					if (in_array($remotename,$availremotename)){
						$info['rssi'][$remotename] = $remoterssi;
					}
				}
			}
		$eqLogics[$eqLogic->getName().' ['.$object.']']=$info;
		}
		return [$eqLogics,$antennas];
	}

	public static function health() {
        $return = array();
		$remotes = blea_remote::getCacheRemotes('allremotes',array());
		if (count($remotes) !=0){
			$return[] = array(
				'test' => __('Nombre d\'antennes', __FILE__),
				'result' => count($remotes),
				'advice' =>  '',
				'state' => True,
			);
			foreach ($remotes as $remote){
				$last = $remote->getCache('lastupdate','0');
				$name = $remote->getRemoteName();
				if ($last == '0' or time() - strtotime($last)>60){
					$result = 'NOK';
					$advice = __('Vérifier le démon sur votre antenne',__FILE__);
					$state = False;
				} else {
					$result = 'OK';
					$advice = '';
					$state = True;
				}
				$return[] = array(
					'test' => __('Démon ' . $name, __FILE__),
					'result' => $result,
					'advice' =>  $advice,
					'state' =>$state,
				);
			}
		}
        return $return;
    }

	public static function sendRemoteFiles($_remoteId) {
		blea::stopremote($_remoteId);
		$remoteObject = blea_remote::byId($_remoteId);
		$user=$remoteObject->getConfiguration('remoteUser');
		$script_path = dirname(__FILE__) . '/../../resources/';
		log::add('blea','info','Compression du dossier local');
		exec('tar -zcvf /tmp/folder-blea.tar.gz ' . $script_path);
		log::add('blea','info','Envoie du fichier  /tmp/folder-blea.tar.gz');
		$result = false;
		$result = $remoteObject->execCmd(['rm -Rf /home/'.$user.'/blead','mkdir -p /home/'.$user.'/blead']);
		if ($remoteObject->sendFiles('/tmp/folder-blea.tar.gz','/home/'.$user.'/folder-blea.tar.gz')) {
			log::add('blea','info',__('Décompression du dossier distant',__FILE__));
			$result = $remoteObject->execCmd(['tar -zxf /home/'.$user.'/folder-blea.tar.gz -C /home/'.$user.'/blead','rm -f /home/'.$user.'/folder-blea.tar.gz']);
		}
		log::add('blea','info',__('Suppression du zip local',__FILE__));
		exec('rm -f /tmp/folder-blea.tar.gz');
		log::add('blea','info',__('Finie',__FILE__));
		return $result;
	}

	public static function getRemoteLog($_remoteId,$_dependancy='') {
		$remoteObject = blea_remote::byId($_remoteId);
		$name = $remoteObject->getRemoteName();
		$local = dirname(__FILE__) . '/../../../../log/blea_'.str_replace(' ','-',$name).$_dependancy;
		log::add('blea','info','Suppression de la log ' . $local);
		exec('rm -f '. $local);
		log::add('blea','info',__('Récupération de la log distante',__FILE__));
		if ($remoteObject->getFiles($local,'/tmp/blea'.$_dependancy)) {
			$remoteObject->execCmd(['cat /dev/null > /tmp/blea'.$_dependancy]);
			return true;
		}
		return false;
	}

	public static function dependancyRemote($_remoteId) {
		blea::stopremote($_remoteId);
		$remoteObject = blea_remote::byId($_remoteId);
		$user=$remoteObject->getConfiguration('remoteUser');
		log::add('blea','info',__('Installation des dépendances',__FILE__));
		return $remoteObject->execCmd(['bash /home/'.$user.'/blead/resources/install_apt.sh  >> ' . '/tmp/blea_dependancy' . ' 2>&1 &']);
	}

	public static function launchremote($_remoteId) {
		log::add('blea','info',__('Lancement du démon distant',__FILE__));
		$remoteObject = blea_remote::byId($_remoteId);
		$last = $remoteObject->getCache('lastupdate','0');
		blea::stopremote($_remoteId);
		sleep(5);
		$user=$remoteObject->getConfiguration('remoteUser');
		$device=$remoteObject->getConfiguration('remoteDevice');
		$script_path = '/home/'.$user.'/blead/resources/blead';
		$cmd = '/usr/bin/python3 ' . $script_path . '/blead.py';
		$cmd .= ' --loglevel ' . log::convertLogLevel(log::getLogLevel('blea'));
		$cmd .= ' --device ' . $device;
		$cmd .= ' --socketport ' . config::byKey('socketport', 'blea');
		$cmd .= ' --sockethost ""';
		$cmd .= ' --callback ' . network::getNetworkAccess('internal') . '/plugins/blea/core/php/jeeBlea.php';
		$cmd .= ' --apikey ' . jeedom::getApiKey('blea');
		$cmd .= ' --daemonname "' . $remoteObject->getRemoteName() . '"';
		$cmd .= ' --noseeninterval ' . config::byKey('absentnumber', 'blea', 4);
		$cmd .= ' --scaninterval ' . config::byKey('scaninterval', 'blea', 29);
		$cmd .= ' --scanmode ' . config::byKey('scanmode', 'blea', 'passive');
		$cmd .= ' >> ' . '/tmp/blea' . ' 2>&1 &';
		log::add('blea','info','Lancement du démon distant ' . $cmd);
		blea_remote::setCacheRemotes('allremotes',blea_remote::all());
		config::save('include_mode', 0, 'blea');
		return $remoteObject->execCmd([$cmd]);
	}

	public static function remotelearn($_remoteId,$_state) {
		$remoteObject = blea_remote::byId($_remoteId);
		$ip = $remoteObject->getConfiguration('remoteIp');
		if ($_state == '1'){
			$allowAll = config::byKey('allowAllinclusion', 'blea');
			$value = array('apikey' => jeedom::getApiKey('blea'), 'cmd' => 'learnin', 'allowAll' => $allowAll);
		} else {
			$value = array('apikey' => jeedom::getApiKey('blea'), 'cmd' => 'learnout');
		}
		$value = json_encode($value);
		$last = $remoteObject->getCache('lastupdate','0');
		if ($last == '0' or time() - strtotime($last)>65){
				return;
		} else {
			$socket = socket_create(AF_INET, SOCK_STREAM, 0);
			socket_connect($socket, $ip, config::byKey('socketport', 'blea'));
			socket_write($socket, $value, strlen($value));
			socket_close($socket);
		}
		return True;
	}

	public static function stopremote($_remoteId) {
		log::add('blea','info',__('Arret du démon distant',__FILE__));
		$remoteObject = blea_remote::byId($_remoteId);
		$ip = $remoteObject->getConfiguration('remoteIp');
		$value = array('apikey' => jeedom::getApiKey('blea'), 'cmd' => 'stop');
		$value = json_encode($value);
		$socket = socket_create(AF_INET, SOCK_STREAM, 0);
		if ($socket) {
			if (@socket_connect($socket, $ip, config::byKey('socketport', 'blea'))) {
				socket_write($socket, $value, strlen($value));
				socket_close($socket);
			}
		}
		$remoteObject->execCmd(['fuser -k 55008/tcp >> /dev/null 2>&1 &']);
		config::save('include_mode', 0, 'blea');
		event::add('blea::includeState', array(
		'mode' => 'learn',
		'state' => 0)
		);
		return True;
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
		if (config::byKey('noLocal', 'blea', 0) == 1){
			$return['state'] = 'ok';
			$return['launchable'] = 'ok';
			return $return;
		}
		$pid_file = jeedom::getTmpFolder('blea') . '/deamon.pid';
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
		$return['progress_file'] = jeedom::getTmpFolder('blea') . '/dependance';
		$return['state'] = 'ok';
		if (exec(system::getCmdSudo() . system::get('cmd_check') . '-E "python3\-serial|python3\-requests|python3\-pyudev|rfkill" | wc -l') < 4) {
			$return['state'] = 'nok';
		}
		if (exec(system::getCmdSudo() . 'pip3 list | grep -E "pyudev|pyserial|requests|bluepy" | wc -l') < 4) {
			$return['state'] = 'nok';
		}
		if ($return['state'] == 'ok') {
			$bluepyversion = exec(system::getCmdSudo() . "pip3 list --format=columns | grep bluepy | awk '{print $2}'");
			if ($bluepyversion <> blea::$_bluepy_version){
				log::add('blea','error', 'Bluepy not up to date : ' . $bluepyversion . ' expected ' . blea::$_bluepy_version);
			}
		}
		return $return;
	}

	public static function dependancy_install() {
		log::remove(__CLASS__ . '_update');
		return array('script' => dirname(__FILE__) . '/../../resources/install_#stype#.sh ' . jeedom::getTmpFolder('blea') . '/dependance', 'log' => log::getPathToLog(__CLASS__ . '_update'));
	}
	public static function deamon_start() {
		self::deamon_stop();
		$deamon_info = self::deamon_info();
		if ($deamon_info['launchable'] != 'ok') {
			throw new Exception(__('Veuillez vérifier la configuration', __FILE__));
		}
		$unlock = exec('sudo rfkill unblock all >/dev/null 2>&1');
		if (config::byKey('port', 'blea','none') == 'none') {
			foreach (jeedom::getBluetoothMapping() as $name => $value) {
				config::save('port', $name ,'blea');
			break;
			}
		}
		$port = jeedom::getBluetoothMapping(config::byKey('port', 'blea'));
		$blea_path = realpath(dirname(__FILE__) . '/../../resources/blead');
		$cmd = 'sudo /usr/bin/python3 ' . $blea_path . '/blead.py';
		$cmd .= ' --loglevel ' . log::convertLogLevel(log::getLogLevel('blea'));
		$cmd .= ' --device ' . $port;
		$cmd .= ' --socketport ' . config::byKey('socketport', 'blea');
		$cmd .= ' --sockethost 127.0.0.1';
		$cmd .= ' --callback ' . network::getNetworkAccess('internal', 'proto:127.0.0.1:port:comp') . '/plugins/blea/core/php/jeeBlea.php';
		$cmd .= ' --apikey ' . jeedom::getApiKey('blea');
		$cmd .= ' --daemonname local';
		$cmd .= ' --noseeninterval ' . config::byKey('absentnumber', 'blea', 4);
		$cmd .= ' --scaninterval ' . config::byKey('scaninterval', 'blea', 29);
		$cmd .= ' --scanmode ' . config::byKey('scanmode', 'blea', 'passive');
		$cmd .= ' --pid ' . jeedom::getTmpFolder('blea') . '/deamon.pid';
		log::add('blea', 'info', 'Lancement démon blea : ' . $cmd);
		$result = exec($cmd . ' >> ' . log::getPathToLog('blea_local') . ' 2>&1 &');
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
			log::add('blea', 'error', __('Impossible de lancer le démon blea, vérifiez la log',__FILE__), 'unableStartDeamon');
			return false;
		}
		blea_remote::setCacheRemotes('allremotes',blea_remote::all());
		blea::launch_allremotes();
		message::removeAll('blea', 'unableStartDeamon');
		config::save('include_mode', 0, 'blea');
		return true;
	}

	public static function syncconfBlea($_background = true) {
		log::remove('blea_syncconf');
		log::add('blea_syncconf', 'info', 'Arrêt du démon en cours');
		self::deamon_stop();
		log::add('blea_syncconf', 'info', 'Arrêt du démon fait');
		$cmd = system::getCmdSudo() . ' /bin/bash ' . dirname(__FILE__) . '/../../resources/syncconf.sh >> ' . log::getPathToLog('blea_syncconf') . ' 2>&1';
		if ($_background) {
			$cmd .= ' &';
		}
		log::add('blea_syncconf', 'info', $cmd);
		shell_exec($cmd);
		self::send_allremotes();
		self::deamon_start();
	}

	public static function sendIdToDeamon() {
		foreach (self::byType('blea') as $eqLogic) {
			$eqLogic->allowDevice();
			usleep(500);
		}
		$value = json_encode(array('apikey' => jeedom::getApiKey('blea'), 'cmd' => 'ready'));
		log::add('blea', 'info', 'Sending ready to daemons');
		self::socket_connection($value,True);
	}

	public function launch_allremotes(){
		log::add('blea','info','Launching remotes ...');
		$remotes = blea_remote::all();
		foreach ($remotes as $remote) {
			blea::launchremote($remote->getId());
			sleep(1);
		}
	}

	public function send_allremotes(){
		log::add('blea','info','Updating files on remotes ...');
		$remotes = blea_remote::all();
		foreach ($remotes as $remote) {
			blea::sendRemoteFiles($remote->getId());
			blea::launchremote($remote->getId());
		}
	}

	public function update_allremotes(){
		log::add('blea','info','Updating remotes ...');
		$remotes = blea_remote::all();
		foreach ($remotes as $remote) {
			blea::dependancyRemote($remote->getId());
			blea::launchremote($remote->getId());
		}
	}

	public function stop_allremotes(){
		log::add('blea','info','Stopping remotes ...');
		$remotes = blea_remote::all();
		foreach ($remotes as $remote) {
			blea::stopremote($remote->getId());
		}
	}

	public static function saveAntennaPosition($_antennas, $_type = ''){
		$remotes = blea_remote::all();
		$antennas = json_decode($_antennas, true);
		foreach ($antennas as $antenna => $position) {
			$name = $antenna;
			$x= explode('|',$position)[0];
			$y= explode('|',$position)[1];
			if ($name == 'local'){
				config::save('positionx'.$_type, $x, 'blea');
				config::save('positiony'.$_type, $y, 'blea');
			} else {
				foreach ($remotes as $remote) {
					if (is_object($remote) && $name == $remote->getRemoteName()){
						$remote->setConfiguration('positionx'.$_type,$x);
						$remote->setConfiguration('positiony'.$_type,$y);
						$remote->save();
						break;
					}
				}
			}
		}
	}

	public static function socket_connection($_value,$_allremotes = False) {
		if (config::byKey('port', 'blea', 'none') != 'none') {
			$socket = socket_create(AF_INET, SOCK_STREAM, 0);
			socket_connect($socket, '127.0.0.1', config::byKey('socketport', 'blea'));
			socket_write($socket, $_value, strlen($_value));
			socket_close($socket);
		}
		if ($_allremotes){
			$remotes = blea_remote::getCacheRemotes('allremotes',array());
			foreach ($remotes as $remote) {
				$ip = $remote->getConfiguration('remoteIp');
				$last = $remote->getCache('lastupdate','0');
				if ($last == '0' or time() - strtotime($last)>65){
					continue;
				} else {
					$socket = socket_create(AF_INET, SOCK_STREAM, 0);
					socket_connect($socket, $ip, config::byKey('socketport', 'blea'));
					socket_write($socket, $_value, strlen($_value));
					socket_close($socket);
				}
			}
		}
	}

	public static function changeLogLive($_level) {
		$value = array('apikey' => jeedom::getApiKey('blea'), 'cmd' => $_level);
		$value = json_encode($value);
		self::socket_connection($value,True);
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

	public static function changeIncludeState($_state, $_mode, $_type) {
		if ($_mode == 1) {
			if ($_state == 1) {
				$allowAll = config::byKey('allowAllinclusion', 'blea');
				$value = json_encode(array('apikey' => jeedom::getApiKey('blea'), 'cmd' => 'learnin', 'allowAll' => $allowAll, 'type' => $_type));
				self::socket_connection($value,True);
			} else {
				$value = json_encode(array('apikey' => jeedom::getApiKey('blea'), 'cmd' => 'learnout'));
				self::socket_connection($value,True);
			}
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
		$remark = false;
		$json = self::devicesParameters($_conf);
		if (isset($json['compatibility'])) {
			foreach ($json['compatibility'] as $compatibility){
				if ($compatibility['imglink'] == explode('/',$this->getConfiguration('iconModel'))[1]){
					$remark = $compatibility['remark'] . ' | ' . $compatibility['inclusion'];
					break;
				}
			}
		}
		$specificmodal = false;
		if ($this->getConfiguration('specificmodal',0) != 0) {
			$specificmodal = 'blea.' . $this->getConfiguration('device');
		}
		$cancontrol = false;
		if ($this->getConfiguration('cancontrol',0) != 0) {
			$cancontrol = true;
		}
		$canbelocked = false;
		if ($this->getConfiguration('canbelocked',0) != 0) {
			$canbelocked = true;
		}
		return [$modelList, $needsrefresh,$remark,$specificmodal,$cancontrol,$canbelocked];
	}

	public function preSave() {
		$device = self::devicesParameters($this->getConfiguration('device'));
		if (isset($device['configuration']['name'])) {
				$this->setConfiguration('name', $device['configuration']['name']);
		}
	}

	public function postSave() {
		if ($this->getConfiguration('applyDevice') != $this->getConfiguration('device') || $this->getConfiguration('applyModel') != $this->getConfiguration('iconModel')) {
			$this->applyModuleConfiguration();
		} else {
			$this->allowDevice();
			if ($this->getConfiguration('specificclass',0) == 1) {
				$device= $this->getConfiguration('device');
				require_once dirname(__FILE__) . '/../config/devices/'.$device.'/class/'.$device.'.class.php';
				$class= $device.'blea';
				$childrenclass = new $class();
				$childrenclass->postSaveChild($this);
			}
		}
	}

	public function preRemove() {
		$this->disallowDevice();
	}

	public function closestAntenna() {
		$closest = 'local';
		$rssicompare = -200;
		foreach ($this->getCmd() as $cmd){
			if (substr($cmd->getLogicalId(),0,4) == 'rssi'){
				$rssi = $cmd->execCmd();
				if ($rssi > $rssicompare) {
					$rssicompare = $rssi;
					$closest = substr($cmd->getLogicalId(),4);
				}
			}
		}
		return $closest;
	}

	public function computePresence() {
		$globalPresence = 0;
		$presentcmd = $this->getCmd(null, 'present');
		if (!is_object($presentcmd)) {
			$presentcmd = new bleaCmd();
			$presentcmd->setLogicalId('present');
			$presentcmd->setIsVisible(0);
			$presentcmd->setIsHistorized(1);
			$presentcmd->setName(__('Present', __FILE__));
			$presentcmd->setType('info');
			$presentcmd->setSubType('binary');
			$presentcmd->setTemplate('dashboard','line');
			$presentcmd->setTemplate('mobile','line');
			$presentcmd->setEqLogic_id($this->getId());
			$presentcmd->save();
		}
		if ($presentcmd->getConfiguration('returnStateValue') == 0 || $presentcmd->getConfiguration('returnStateTime') == 2){
			$presentcmd->setConfiguration('returnStateValue','');
			$presentcmd->setConfiguration('returnStateTime','');
			$presentcmd->save();
		}
		foreach ($this->getCmd('info') as $cmd) {
			if (substr($cmd->getLogicalId(),0,7) == 'present' && $cmd->getLogicalId()!= 'present'){
				$globalPresence += $cmd->execCmd();
			}
		}
		if ($globalPresence > 0) {
			$this->checkAndUpdateCmd($presentcmd, 1);
		} else {
			$this->checkAndUpdateCmd($presentcmd, 0);
		}
	}

	public function allowDevice() {
		$value = array('apikey' => jeedom::getApiKey('blea'), 'cmd' => 'add');
		$islocked =0;
		$emitter = 'local';
		if ($this->getConfiguration('islocked',0)==1){
			if ($this->getConfiguration('antenna','local') == 'all'){
				$islocked = 0;
				$emitter = 'all';
			} else if ($this->getConfiguration('antenna','local') == 'local'){
				$islocked = 1;
				$emitter = 'local';
			} else {
				$islocked = 1;
				$emitterAntenna = blea_remote::byId($this->getConfiguration('antenna','local'));
				if (is_object($emitterAntenna)){
					$emitter = $emitterAntenna->getRemoteName();
				} else {
					log::add('blea','error','Attention l\'antenne définie en émission pour ' . $this->getHumanName() . ' n\'existe plus.');
					$emitter = 'unknown';
				}
			}
		} else {
			if ($this->getConfiguration('antenna','local') == 'all'){
				$emitter = 'all';
			} else if ($this->getConfiguration('antenna','local') == 'local'){
				$emitter = 'local';
			} else {
				$emitterAntenna = blea_remote::byId($this->getConfiguration('antenna','local'));
				if (is_object($emitterAntenna)){
					$emitter = $emitterAntenna->getRemoteName();
				} else {
					log::add('blea','error','Attention l\'antenne définie en émission pour ' . $this->getHumanName() . ' n\'existe plus.');
					$emitter = 'unknown';
				}
			}
		}
		if ($this->getConfiguration('antennareceive','local') == 'local' || $this->getConfiguration('antennareceive','local') == 'all'){
			$refresher = $this->getConfiguration('antennareceive','local');
		} else {
			$refresherAntenna = blea_remote::byId($this->getConfiguration('antennareceive','local'));
			if (is_object($refresherAntenna)){
				$refresher = $refresherAntenna->getRemoteName();
			} else {
				log::add('blea','error','Attention l\'antenne définie en réception pour ' . $this->getHumanName() . ' n\'existe plus.');
				$refresher = 'unknown';
			}
		}
		if ($this->getLogicalId() != '') {
			$value['device'] = array(
				'id' => $this->getLogicalId(),
				'delay' => intval($this->getConfiguration('delay',0)),
				'needsrefresh' => intval($this->getConfiguration('needsrefresh',0)),
				'name' => $this->getConfiguration('name','0'),
				'refreshlist' => $this->getConfiguration('refreshlist',array()),
				'islocked' => $islocked,
				'emitterallowed' => $emitter,
				'refresherallowed' => $refresher,
				'specificconfiguration' => $this->getConfiguration('specificconfiguration',array()),
				'absent' => $this->getConfiguration('absent',''),
				'type' => $this->getConfiguration('type',''),
				'model' => $this->getConfiguration('iconModel',''),
			);
			$value = json_encode($value);
			self::socket_connection($value,True);
		}
	}

	public function disallowDevice() {
		if ($this->getLogicalId() == '') {
			return;
		}
		$value = json_encode(array('apikey' => jeedom::getApiKey('blea'), 'cmd' => 'remove', 'device' => array('id' => $this->getLogicalId())));
		self::socket_connection($value,True);
	}

	public function applyModuleConfiguration() {
		$device = self::devicesParameters($this->getConfiguration('device'));
		if (!is_array($device)) {
			return true;
		}
		$this->setConfiguration('canbelocked',0);
		$this->setConfiguration('cancontrol',0);
		$this->setConfiguration('islocked',0);
		$this->setConfiguration('name','0');
		$this->setConfiguration('refreshlist',array());
		$this->setConfiguration('specificmodal',0);
		$this->setConfiguration('specificclass',0);
		$this->setConfiguration('needsrefresh',0);
		$this->setConfiguration('resetRssis',1);
		$this->setConfiguration('specificwidgets',0);
		$this->setConfiguration('applyDevice', $this->getConfiguration('device'));
		$this->setConfiguration('applyModel', $this->getConfiguration('iconModel'));
		$this->save();
		if ($this->getConfiguration('device') == '') {
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
		$model=$this->getConfiguration('iconModel','');
		if (isset($device['models'])) {
			if (isset($device['models'][$model])) {
				foreach ($device['models'][$model]['configuration'] as $key => $value) {
					$this->setConfiguration($key, $value);
				}
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
			if (!(in_array($this->getConfiguration('device'), array('miscale','miscale2')))){
				foreach ($arrayToRemove as $cmdToRemove) {
					try {
						$cmdToRemove->remove();
					} catch (Exception $e) {

					}
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
		sleep(2);
		event::add('jeedom::alert', array(
			'level' => 'warning',
			'page' => 'blea',
			'message' => '',
		));
	}

	public function toHtml($_version = 'dashboard') {
		if ($this->getConfiguration('specificwidgets',0) == 1) {
			if ($this->getConfiguration('specificclass',0) == 1) {
				$device= $this->getConfiguration('device');
				require_once dirname(__FILE__) . '/../config/devices/'.$device.'/class/'.$device.'.class.php';
				$class= $device.'blea';
				$childrenclass = new $class();
				return $childrenclass->convertHtml($this,$_version);
			} else {
				$replace = $this->preToHtml($_version);
				if (!is_array($replace)) {
					return $replace;
				}
				$version = jeedom::versionAlias($_version);
				foreach ($this->getCmd() as $cmd) {
					if ($cmd->getType() == 'info') {
						$replace['#' . $cmd->getLogicalId() . '_history#'] = '';
						$replace['#' . $cmd->getLogicalId() . '#'] = $cmd->execCmd();
						$replace['#' . $cmd->getLogicalId() . '_id#'] = $cmd->getId();
						$replace['#' . $cmd->getLogicalId() . '_collectDate#'] = $cmd->getCollectDate();
						if ($cmd->getIsHistorized() == 1) {
							$replace['#' . $cmd->getLogicalId() . '_history#'] = 'history cursor';
						}
					} else {
						$replace['#' . $cmd->getLogicalId() . '_id#'] = $cmd->getId();
					}
				}
				return $this->postToHtml($_version, template_replace($replace, getTemplate('core', $version, $this->getConfiguration('device'), 'blea')));
			}
		} else {
			return parent::toHtml($_version);
		}
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
		if ($eqLogic->getConfiguration('specificclass',0) != 0) {
			$device= $eqLogic->getConfiguration('device');
			require_once dirname(__FILE__) . '/../config/devices/'.$device.'/class/'.$device.'.class.php';
			$class= $device.'blea';
			$childrenclass = new $class();
		}
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
					case 'select':
						$data[trim($value[0])] = trim(str_replace('#listValue#', $_options['select'], $value[1]));
						break;
					case 'message':
						$data[trim($value[0])] = trim(str_replace('#message#', $_options['message'], $value[1]));
						$data[trim($value[0])] = trim(str_replace('#title#', $_options['title'], $data[trim($value[0])]));
						break;
					default:
						$data[trim($value[0])] = trim($value[1]);
				}
			}
		}
		if (isset($data['secondary'])){
			$data['secondary'] = $eqLogic->getCmd('info',$data['secondary'])->execCmd();
		}
		if (isset($data['classlogical'])){
			$data = $childrenclass->calculateOutputValue($eqLogic,$data,$_options);
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
		if ($this->getLogicalId() == 'refresh' || $this->getLogicalId() == 'helper' || $this->getLogicalId() == 'helperrandom'){
			$data['name'] = $eqLogic->getConfiguration('name','0');
			$value = json_encode(array('apikey' => jeedom::getApiKey('blea'), 'cmd' => $this->getLogicalId(), 'device' => array('id' => $eqLogic->getLogicalId()), 'command' => $data));
		} else {
			$value = json_encode(array('apikey' => jeedom::getApiKey('blea'), 'cmd' => 'action', 'device' => array('id' => $eqLogic->getLogicalId()), 'command' => $data));
		}
		$sender = $eqLogic->getConfiguration('antenna','local');
		if ($sender == 'local'){
			log::add('blea','info','Envoi depuis local');
			blea::socket_connection($value);
		} elseif ($sender == 'all') {
			$closest = $eqLogic->closestAntenna();
			if ($closest == 'local'){
				log::add('blea','info',__('Envoi depuis local car plus proche',__FILE__));
				blea::socket_connection($value);
			} else {
				$remotes = blea_remote::all();
				foreach ($remotes as $remote){
					if (is_object($remote) && $remote->getRemoteName() == $closest){
						log::add('blea','info',__('Envoi depuis ',__FILE__) . $remote->getRemoteName() . __(' car plus proche',__FILE__));
						$ip = $remote->getConfiguration('remoteIp');
						$socket = socket_create(AF_INET, SOCK_STREAM, 0);
						socket_connect($socket, $ip, config::byKey('socketport', 'blea'));
						socket_write($socket, $value, strlen($value));
						socket_close($socket);
						break;
					}
				}
			}
		} else {
			$remote = blea_remote::byId($sender);
			if (is_object($remote)){
				log::add('blea','info',__('Envoi depuis ',__FILE__) . $remote->getRemoteName());
				$ip = $remote->getConfiguration('remoteIp');
				$socket = socket_create(AF_INET, SOCK_STREAM, 0);
				socket_connect($socket, $ip, config::byKey('socketport', 'blea'));
				socket_write($socket, $value, strlen($value));
				socket_close($socket);
			}
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
		DB::save($this);
		self::setCacheRemotes('allremotes',self::all());
		return;
	}

	public function remove() {
		return DB::remove($this);
	}

	public function getCache($_key = '', $_default = '') {
		$cache = cache::byKey('eqLogicCacheAttr' . $this->getId())->getValue();
		return utils::getJsonAttr($cache, $_key, $_default);
	}

	public function setCache($_key, $_value = null) {
		cache::set('eqLogicCacheAttr' . $this->getId(), utils::setJsonAttr(cache::byKey('eqLogicCacheAttr' . $this->getId())->getValue(), $_key, $_value));
	}

	public static function getCacheRemotes($_key = '', $_default = '') {
		$cache = cache::byKey('BleaPluginRemotes')->getValue();
		return utils::getJsonAttr($cache, $_key, $_default);
	}

	public static function setCacheRemotes($_key, $_value = null) {
		cache::set('BleaPluginRemotes', utils::setJsonAttr(cache::byKey('BleaPluginRemotes')->getValue(), $_key, $_value));
	}

	public function execCmd($_cmd) {
		$ip = $this->getConfiguration('remoteIp');
		$port = $this->getConfiguration('remotePort');
		$user = $this->getConfiguration('remoteUser');
		$pass = $this->getConfiguration('remotePassword');
		if (!$connection = ssh2_connect($ip, $port)) {
			log::add('blea', 'error', 'connexion SSH KO for ' . $this->remoteName);
				return false;
		} else {
			if (!ssh2_auth_password($connection, $user, $pass)) {
				log::add('blea', 'error', 'Authentification SSH KO for ' . $this->remoteName);
				return false;
			} else {
				foreach ($_cmd as $cmd){
					log::add('blea', 'info', __('Commande par SSH ',__FILE__) . $cmd .  __(' sur ',__FILE__) . $ip);
					$execmd = "echo '" . $pass . "' | sudo -S " . $cmd;
					$stream = ssh2_exec($connection, $execmd);
					$errorStream = ssh2_fetch_stream($stream, SSH2_STREAM_STDERR);
					stream_set_blocking($errorStream, true);
					stream_set_blocking($stream, true);
					$output = stream_get_contents($stream) . ' ' . stream_get_contents($errorStream);
					fclose($stream);
					fclose($errorStream);
					if (trim($output) != '') {
						log::add('blea','debug',$output);
					}
				}
				$stream = ssh2_exec($connection, 'exit');
				$errorStream = ssh2_fetch_stream($stream, SSH2_STREAM_STDERR);
				stream_set_blocking($errorStream, true);
				stream_set_blocking($stream, true);
				$output = stream_get_contents($stream) . ' ' . stream_get_contents($errorStream);
				fclose($stream);
				fclose($errorStream);
				if (trim($output) != '') {
					log::add('blea','debug',$output);
				}
				return $output !== false;
			}
		}
	}

	public function sendFiles($_local, $_target) {
		$ip = $this->getConfiguration('remoteIp');
		$port = $this->getConfiguration('remotePort');
		$user = $this->getConfiguration('remoteUser');
		$pass = $this->getConfiguration('remotePassword');
		if (!$connection = ssh2_connect($ip, $port)) {
			log::add('blea', 'error', 'connexion SSH KO for ' . $this->remoteName);
			return false;
		} else {
			if (!ssh2_auth_password($connection, $user, $pass)) {
				log::add('blea', 'error', 'Authentification SSH KO for ' . $this->remoteName);
				return false;
			} else {
				log::add('blea', 'info', 'Envoie de fichier sur ' . $ip);
				$result = ssh2_scp_send($connection, $_local, $_target, 0777);
				if (!$result){
					log::add('blea','error','Files could not be sent to ' . $ip);
					return false;
				} else {
					log::add('blea','info','Files successfully sent to ' . $ip);
				}
				$execmd = "echo '" . $pass . "' | sudo -S " . 'exit';
				$stream = ssh2_exec($connection, $execmd);
				$errorStream = ssh2_fetch_stream($stream, SSH2_STREAM_STDERR);
				stream_set_blocking($errorStream, true);
				stream_set_blocking($stream, true);
				$output = stream_get_contents($stream);
				fclose($stream);
				fclose($errorStream);
				if (trim($output) != '') {
					log::add('blea','debug',$output);
				}
			}
		}
		return true;
	}

	public function getFiles($_local, $_target) {
		$ip = $this->getConfiguration('remoteIp');
		$port = $this->getConfiguration('remotePort');
		$user = $this->getConfiguration('remoteUser');
		$pass = $this->getConfiguration('remotePassword');
		if (!$connection = ssh2_connect($ip, $port)) {
			log::add('blea', 'error', 'connexion SSH KO for ' . $this->remoteName);
				return false;
		} else {
			if (!ssh2_auth_password($connection, $user, $pass)) {
				log::add('blea', 'error', 'Authentification SSH KO for ' . $this->remoteName);
				return false;
			} else {
				log::add('blea', 'info', __('Récupération de fichier depuis ',__FILE__) . $ip);
				$result = ssh2_scp_recv($connection, $_target, $_local);
				$execmd = "echo '" . $pass . "' | sudo -S " . 'exit';
				$stream = ssh2_exec($connection, $execmd);
				$errorStream = ssh2_fetch_stream($stream, SSH2_STREAM_STDERR);
				stream_set_blocking($errorStream, true);
				stream_set_blocking($stream, true);
				$output = stream_get_contents($stream);
				fclose($stream);
				fclose($errorStream);
				if (trim($output) != '') {
					log::add('blea','debug',$output);
				}
			}
		}
		return true;
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
