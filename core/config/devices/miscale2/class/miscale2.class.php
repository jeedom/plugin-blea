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

class miscale2blea extends blea {

	public static function saveUserList($_id, $_userList) {
		$datas = array('impedance' =>  array('name' => 'Impédance', 'unit' => 'ohm', 'type' => 'numeric'),
						'lbm' =>  array('name' => 'LBM', 'unit' => 'kg', 'type' => 'numeric'),
						'fat' =>  array('name' => 'Taux graisse', 'unit' => '%', 'type' => 'numeric'),
						'water' =>  array('name' => 'Taux eau', 'unit' => '%', 'type' => 'numeric'),
						'bones' =>  array('name' => 'Masse Os', 'unit' => 'kg', 'type' => 'numeric'),
						'muscle' =>  array('name' => 'Masse Muscle', 'unit' => 'kg', 'type' => 'numeric'),
						'visceral' =>  array('name' => 'Visceral', 'unit' => 'kg', 'type' => 'numeric'),
						'imc' =>  array('name' => 'IMC', 'unit' => '', 'type' => 'numeric'),
						'bmr' =>  array('name' => 'BMR', 'unit' => 'kcal', 'type' => 'numeric'),
						'ideal' =>  array('name' => 'Idéal', 'unit' => 'kg', 'type' => 'numeric'),
						'body' =>  array('name' => 'Type', 'unit' => '', 'type' => 'string'),
						'fatmassideal' =>  array('name' => 'Masse vers idéal', 'unit' => 'kg', 'type' => 'numeric'),
						'protein' => array('name' => 'Taux Protéine', 'unit' => '%', 'type' => 'numeric'),
						'imclabel' => array('name' => 'IMC Label', 'unit' => '', 'type' => 'string'),
				);
		$miscale = blea::byId($_id);
		$userList = json_decode($_userList,true);
		$newList = array();
		foreach ($userList as $key=>$user){
			$newList[$key] = array(
				'name' => $user['name'],
				'height' =>$user['height'],
				'weight' =>$user['weight'],
				'sex' =>$user['sex'],
				'age' =>$user['age'],
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
			foreach ($datas as $key => $value){
				$userCmd = $miscale->getCmd('info',$key.$user['name']);
				if (!is_object($userCmd)){
					$userCmd = new bleaCmd();
					$userCmd->setLogicalId($key.$user['name']);
					$userCmd->setIsVisible(1);
					$userCmd->setIsHistorized(1);
					$userCmd->setName(__($value['name'] . ' ' . $user['name'], __FILE__));
					$userCmd->setType('info');
					$userCmd->setSubType($value['type']);
					$userCmd->setUnite($value['unit']);
					$userCmd->setTemplate('mobile','line');
					$userCmd->setTemplate('dashboard','line');
					$userCmd->setEqLogic_id($miscale->getId());
					$userCmd->save();
				}
			}
		}
		$miscale->setConfiguration('specificconfiguration',$newList);
		$miscale->save();
		return True;
	}
	
	public static function calculateInputValue($_eqLogic,$_datas) {
		$listUsers = $_eqLogic->getConfiguration('specificconfiguration',array());
		foreach ($listUsers as $id => $data) {
			$name = $data['name'];
			if (isset($_datas['poids'.$name])){
				$listUsers[$name]['weight'] = $_datas['poids'.$name];
				$_eqLogic->setConfiguration('specificconfiguration',$listUsers);
				$_eqLogic->save();
			}
		}
		return $_datas;
	}
	
	public static function postSaveChild($_eqLogic) {
		$datas = array('impedance' =>  array('name' => 'Impédance', 'unit' => 'ohm', 'type' => 'numeric'),
						'lbm' =>  array('name' => 'LBM', 'unit' => 'kg', 'type' => 'numeric'),
						'fat' =>  array('name' => 'Taux graisse', 'unit' => '%', 'type' => 'numeric'),
						'water' =>  array('name' => 'Taux eau', 'unit' => '%', 'type' => 'numeric'),
						'bones' =>  array('name' => 'Masse Os', 'unit' => 'kg', 'type' => 'numeric'),
						'muscle' =>  array('name' => 'Masse Muscle', 'unit' => 'kg', 'type' => 'numeric'),
						'visceral' =>  array('name' => 'Visceral', 'unit' => 'kg', 'type' => 'numeric'),
						'imc' =>  array('name' => 'IMC', 'unit' => '', 'type' => 'numeric'),
						'bmr' =>  array('name' => 'BMR', 'unit' => 'kcal', 'type' => 'numeric'),
						'ideal' =>  array('name' => 'Idéal', 'unit' => 'kg', 'type' => 'numeric'),
						'body' =>  array('name' => 'Type', 'unit' => '', 'type' => 'string'),
						'fatmassideal' =>  array('name' => 'Masse vers idéal', 'unit' => 'kg', 'type' => 'numeric'),
						'protein' => array('name' => 'Taux Protéine', 'unit' => '%', 'type' => 'numeric'),
						'imclabel' => array('name' => 'IMC Label', 'unit' => '', 'type' => 'string'),
				);
		$listUsers = $_eqLogic->getConfiguration('specificconfiguration',array());
		foreach ($listUsers as $key=>$user){
			$userweigthCmd = $_eqLogic->getCmd('info','poids'.$user['name']);
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
				$userweigthCmd->setEqLogic_id($_eqLogic->getId());
				$userweigthCmd->save();
			}
			$userweigthCmd->event($user['weight']);
			foreach ($datas as $key => $value){
				$userCmd = $_eqLogic->getCmd('info',$key.$user['name']);
				if (!is_object($userCmd)){
					$userCmd = new bleaCmd();
					$userCmd->setLogicalId($key.$user['name']);
					$userCmd->setIsVisible(1);
					$userCmd->setIsHistorized(1);
					$userCmd->setName(__($value['name'] . ' ' . $user['name'], __FILE__));
					$userCmd->setType('info');
					$userCmd->setSubType($value['type']);
					$userCmd->setUnite($value['unit']);
					$userCmd->setTemplate('mobile','line');
					$userCmd->setTemplate('dashboard','line');
					$userCmd->setEqLogic_id($_eqLogic->getId());
					$userCmd->save();
				}
			}
		}
	}
}

?>
