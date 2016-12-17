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

class miscaleblea extends blea {

	public static function saveUserList($_id, $_userList) {
		$miscale = blea::byId($_id);
		$userList = json_decode($_userList,true);
		$newList = array();
		foreach ($userList as $key=>$user){
			$newList[$key] = array(
				'name' => $user['name'],
				'height' =>$user['height'],
				'weight' =>$user['weight'],
			);
			$userweigthCmd = $miscale->getCmd('info','poids'.$user['name']);
			if (!is_object($userweigthCmd)){
				$userweigthCmd = new bleaCmd();
				$userweigthCmd->setLogicalId('poids'.$user['name']);
				$userweigthCmd->setIsVisible(1);
				$userweigthCmd->setIsHistorized(1);
				$userweigthCmd->setName(__('Poids ' . $user['name'], __FILE__));
				$userweigthCmd->setType('info');
				$userweigthCmd->setSubType('numeric');
				$userweigthCmd->setUnite('kg');
				$userweigthCmd->setTemplate('mobile','line');
				$userweigthCmd->setTemplate('dashboard','line');
				$userweigthCmd->setEqLogic_id($miscale->getId());
				$userweigthCmd->save();
			}
			$userweigthCmd->event($user['weight']);
			$userimcCmd = $miscale->getCmd('info','imc'.$user['name']);
			if (!is_object($userimcCmd)){
				$userimcCmd = new bleaCmd();
				$userimcCmd->setLogicalId('imc'.$user['name']);
				$userimcCmd->setIsVisible(1);
				$userimcCmd->setIsHistorized(1);
				$userimcCmd->setName(__('Imc ' . $user['name'], __FILE__));
				$userimcCmd->setType('info');
				$userimcCmd->setSubType('numeric');
				$userimcCmd->setTemplate('mobile','line');
				$userimcCmd->setTemplate('dashboard','line');
				$userimcCmd->setEqLogic_id($miscale->getId());
				$userimcCmd->save();
			}
			$userimcCmd->event(round($user['weight']/($user['height']*$user['height']),2));
		}
		$miscale->setConfiguration('userList',$newList);
		$miscale->save();
		$userlist = $miscale->getConfiguration('userList');
		foreach ($miscale->getCmd('info') as $cmd){
			if (substr($cmd->getLogicalId(),0,3) == 'imc'){
				if (!isset($userlist[substr($cmd->getLogicalId(),3)])) {
					$cmd->remove();
				}
			} else if (substr($cmd->getLogicalId(),0,5) == 'poids' && $cmd->getLogicalId() != 'poids'){
				if (!isset($userlist[substr($cmd->getLogicalId(),5)])) {
					$cmd->remove();
				}
			} 
		}
		return True;
	}
	
	public static function calculateInputValue($_eqLogic,$_datas) {
		if (isset($_datas['poids'])){
			$poids = $_datas['poids'];
			$listUsers = $_eqLogic->getConfiguration('userList',array());
			if (count($listUsers>0)){
				$userArray=array();
				foreach ($listUsers as $id => $data) {
					$name = $data['name'];
					$userweigthCmd = $_eqLogic->getCmd('info','poids'.$name);
					if (is_object($userweigthCmd)){
						$lastKnownWeight = $userweigthCmd->execCmd();
						$userArray[$name] = $lastKnownWeight;
					}
				}
				$target = '';
				$delta = 999;
				foreach ($userArray as $name => $last) {
					$currentdelta = abs($last-$poids);
					if ($currentdelta<$delta){
						$delta = $currentdelta;
						$target = $name;
					}
				}
				if ($target != ''){
					$_datas['poids'.$target] = $poids;
					$_datas['imc'.$target] = round($poids/($listUsers[$target]['height']*$listUsers[$target]['height']),2);
					$listUsers[$target]['weight'] = $poids;
					$_eqLogic->setConfiguration('userList',$listUsers);
					$_eqLogic->save();
				}
			}
		}
		return $_datas;
	}
	
	public static function postSaveChild($_eqLogic) {
		$listUsers = $_eqLogic->getConfiguration('userList',array());
		foreach ($listUsers as $key=>$user){
			$userweigthCmd = $_eqLogic->getCmd('info','poids'.$user['name']);
			if (!is_object($userweigthCmd)){
				$userweigthCmd = new bleaCmd();
				$userweigthCmd->setLogicalId('poids'.$user['name']);
				$userweigthCmd->setIsVisible(0);
				$userweigthCmd->setIsHistorized(1);
				$userweigthCmd->setName(__('Poids ' . $user['name'], __FILE__));
				$userweigthCmd->setType('info');
				$userweigthCmd->setSubType('numeric');
				$userweigthCmd->setUnite('kg');
				$userweigthCmd->setTemplate('mobile','line');
				$userweigthCmd->setTemplate('dashboard','line');
				$userweigthCmd->setEqLogic_id($_eqLogic->getId());
				$userweigthCmd->save();
			}
			$userweigthCmd->event($user['weight']);
			$userimcCmd = $_eqLogic->getCmd('info','imc'.$user['name']);
			if (!is_object($userimcCmd)){
				$userimcCmd = new bleaCmd();
				$userimcCmd->setLogicalId('imc'.$user['name']);
				$userimcCmd->setIsVisible(0);
				$userimcCmd->setIsHistorized(1);
				$userimcCmd->setName(__('Imc ' . $user['name'], __FILE__));
				$userimcCmd->setType('info');
				$userimcCmd->setSubType('numeric');
				$userimcCmd->setTemplate('mobile','line');
				$userimcCmd->setTemplate('dashboard','line');
				$userimcCmd->setEqLogic_id($_eqLogic->getId());
				$userimcCmd->save();
			}
			$userimcCmd->event(round($user['weight']/($user['height']*$user['height']),2));
		}
	}
}

?>
