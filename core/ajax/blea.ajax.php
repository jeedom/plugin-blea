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
	require_once dirname(__FILE__) . '/../../../../core/php/core.inc.php';
	include_file('core', 'authentification', 'php');

	if (!isConnect('admin')) {
		throw new Exception('401 Unauthorized');
	}

	ajax::init();

	if (init('action') == 'changeIncludeState') {
		blea::changeIncludeState(init('state'), init('mode'), init('type'));
		ajax::success();
	}
	
	if (init('action') == 'getAllTypes') {
		$list = array();
		$allconfs = blea::devicesParameters();
		foreach ($allconfs as $key=>$data){
			$list[$data['name']] = $data['configuration']['name'];
		}
		ksort($list);
		ajax::success($list);
	}
	
	if (init('action') == 'allantennas') {
		log::add('blea','error',init('remote') . init('type') . init('remoteId'));
		if (init('remote') == 'local') {
			if (init('type') == 'reception'){
				foreach (eqLogic::byType('blea') as $eqLogic){
					$eqLogic->setConfiguration('antennareceive','local');
					$eqLogic->save();
				}
			} else {
				foreach (eqLogic::byType('blea') as $eqLogic){
					$eqLogic->setConfiguration('antenna','local');
					$eqLogic->save();
				}
			}
		} else {
			if (init('type') == 'reception'){
				foreach (eqLogic::byType('blea') as $eqLogic){
					$eqLogic->setConfiguration('antennareceive',init('remoteId'));
					$eqLogic->save();
				}
			} else {
				foreach (eqLogic::byType('blea') as $eqLogic){
					$eqLogic->setConfiguration('antenna',init('remoteId'));
					$eqLogic->save();
				}
			}
		}
		ajax::success();
	}
	
	if (init('action') == 'syncconfBlea') {
		blea::syncconfBlea(false);
		ajax::success();
	}

	if (init('action') == 'getMobileGraph') {
		ajax::success(blea::getMobileGraph());
	}

	if (init('action') == 'getMobileHealth') {
		ajax::success(blea::getMobileHealth());
	}

	if (init('action') == 'saveAntennaPosition') {
		ajax::success(blea::saveAntennaPosition(init('antennas')));
	}
	
	if (init('action') == 'launchremotes') {
		ajax::success(blea::launch_allremotes());
	}
	
	if (init('action') == 'sendremotes') {
		ajax::success(blea::send_allremotes());
	}

	if (init('action') == 'autoDetectModule') {
		$eqLogic = blea::byId(init('id'));
		if (!is_object($eqLogic)) {
			throw new Exception(__('Blea eqLogic non trouvé : ', __FILE__) . init('id'));
		}
		if (init('createcommand') == 1){
			foreach ($eqLogic->getCmd() as $cmd) {
				$cmd->remove();
			}
		}
		$eqLogic->setConfiguration('applyDevice','');
		$eqLogic->save();
		ajax::success();
	}

	if (init('action') == 'getModelListParam') {
		$blea = blea::byId(init('id'));
		if (!is_object($blea)) {
			ajax::success(array());
		}
		ajax::success($blea->getModelListParam(init('conf')));
	}

	if (init('action') == 'save_bleaRemote') {
		$bleaRemoteSave = jeedom::fromHumanReadable(json_decode(init('blea_remote'), true));
		$blea_remote = blea_remote::byId($bleaRemoteSave['id']);
		if (!is_object($blea_remote)) {
			$blea_remote = new blea_remote();
		}
		utils::a2o($blea_remote, $bleaRemoteSave);
		$blea_remote->save();
		ajax::success(utils::o2a($blea_remote));
	}

	if (init('action') == 'get_bleaRemote') {
		$blea_remote = blea_remote::byId(init('id'));
		if (!is_object($blea_remote)) {
			throw new Exception(__('Remote inconnu : ', __FILE__) . init('id'), 9999);
		}
		ajax::success(jeedom::toHumanReadable(utils::o2a($blea_remote)));
	}

	if (init('action') == 'remove_bleaRemote') {
		$blea_remote = blea_remote::byId(init('id'));
		if (!is_object($blea_remote)) {
			throw new Exception(__('Remote inconnu : ', __FILE__) . init('id'), 9999);
		}
		$blea_remote->remove();
		ajax::success();
	}

	if (init('action') == 'sendRemoteFiles') {
		if (!blea::sendRemoteFiles(init('remoteId'))) {
			ajax::error(__('Erreur, vérifiez la log Blea', __FILE__));
		}
		ajax::success();
    }

	if (init('action') == 'getRemoteLog') {
		if (!blea::getRemoteLog(init('remoteId'))) {
			ajax::error(__('Erreur, vérifiez la log Blea', __FILE__));
		}
		ajax::success();
     }

	 if (init('action') == 'getRemoteLogDependancy') {
		if (!blea::getRemoteLog(init('remoteId'),'_dependancy')) {
			ajax::error(__('Erreur, vérifiez la log Blea', __FILE__));
		}
		ajax::success();
     }

	 if (init('action') == 'launchremote') {
		if (!blea::launchremote(init('remoteId'))) {
			ajax::error(__('Erreur, vérifiez la log Blea', __FILE__));
		}
		ajax::success();
     }

	 if (init('action') == 'stopremote') {
		if (!blea::stopremote(init('remoteId'))) {
			ajax::error(__('Erreur, vérifiez la log Blea', __FILE__));
		}
		ajax::success();
     }

	 if (init('action') == 'remotelearn') {
        ajax::success(blea::remotelearn(init('remoteId'), init('state')));
     }

	 if (init('action') == 'dependancyRemote') {
        ajax::success(blea::dependancyRemote(init('remoteId')));
     }

	 if (init('action') == 'aliveremote') {
        ajax::success(blea::aliveremote(init('remoteId')));
     }

	if (init('action') == 'changeLogLive') {
		ajax::success(blea::changeLogLive(init('level')));
	}

	throw new Exception('Aucune methode correspondante');
	/*     * *********Catch exeption*************** */
} catch (Exception $e) {
	ajax::error(displayExeption($e), $e->getCode());
}
?>
