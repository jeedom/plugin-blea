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

	switch (init('action')) {
	    case 'changeIncludeState' :
		    blea::changeIncludeState(init('state'), init('mode'));
		    ajax::success();
		break;
			
	    case 'getMobileGraph':
		ajax::success(blea::getMobileGraph());
		break;
			
	    case 'getMobileHealth':
		ajax::success(blea::getMobileHealth());
		break;
			
	    case 'saveAntennaPosition':
		ajax::success(blea::saveAntennaPosition(init('antennas')));
		break;
			
	    case 'autoDetectModule':
		$eqLogic = blea::byId(init('id'));
		if (!is_object($eqLogic)) {
		    throw new Exception(__('Blea eqLogic non trouvé : ', __FILE__) . init('id'));
		}
		foreach ($eqLogic->getCmd() as $cmd) {
		    $cmd->remove();
		}
		$eqLogic->applyModuleConfiguration();
		ajax::success();
		break;
			
	    case 'getModelListParam':
		$blea = blea::byId(init('id'));
		if (!is_object($blea)) {
		    ajax::success(array());
		}
		ajax::success($blea->getModelListParam(init('conf')));
		break;
			
	    case 'save_bleaRemote':
		$bleaRemoteSave = jeedom::fromHumanReadable(json_decode(init('blea_remote'), true));
		$blea_remote = blea_remote::byId($bleaRemoteSave['id']);
		if (!is_object($blea_remote)) {
		    $blea_remote = new blea_remote();
		}
		utils::a2o($blea_remote, $bleaRemoteSave);
		$blea_remote->save();
		ajax::success(utils::o2a($blea_remote));
		break;
			
	    case 'get_bleaRemote':
		$blea_remote = blea_remote::byId(init('id'));
		if (!is_object($blea_remote)) {
		    throw new Exception(__('Remote inconnu : ', __FILE__) . init('id'), 9999);
		}
		ajax::success(jeedom::toHumanReadable(utils::o2a($blea_remote)));
		break;
			
            case 'remove_bleaRemote':
		$blea_remote = blea_remote::byId(init('id'));
		if (!is_object($blea_remote)) {
		    throw new Exception(__('Remote inconnu : ', __FILE__) . init('id'), 9999);
		}
		$blea_remote->remove();
		ajax::success();
		break;
			
	    case 'sendRemoteFiles':
		ajax::success(blea::sendRemoteFiles(init('remoteId')));
		break;
			
	    case 'getRemoteLog':
		ajax::success(blea::getRemoteLog(init('remoteId')));
		break;
			
	    case 'getRemoteLogDependancy':
		ajax::success(blea::getRemoteLog(init('remoteId'),'_dependancy'));
		break;
			
	    case 'launchremote':
		ajax::success(blea::launchremote(init('remoteId')));
		break;
			
	    case 'stopremote':
		ajax::success(blea::stopremote(init('remoteId')));
		break;
			
	    case 'remotelearn':
		ajax::success(blea::remotelearn(init('remoteId'), init('state')));
		break;
			
	    case 'dependancyRemote':
		ajax::success(blea::launchremote(init('remoteId')));
		break;
			
	    case 'aliveremote':
		ajax::success(blea::aliveremote(init('remoteId')));
		break;
			
	    case 'changeLogLive':
		ajax::success(blea::changeLogLive(init('level')));
		break;
			
	    default:
		throw new Exception('Aucune methode correspondante');
	}
	
	/*     * *********Catch exeption*************** */
} catch (Exception $e) {
	ajax::error(displayExeption($e), $e->getCode());
}
 
