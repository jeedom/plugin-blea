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

class aqualinblea extends blea {

    public static function cronDispatcher($_params) {
        $blea = blea::byId($_params['aqualin_id']);
        $cmd = $blea->getCmd('action','name:aqualin,classlogical:sendraw,handle:0x2a,type:display,value:calcul');
        if (is_object($cmd)){
            $cmd->execute(array('message' => $blea->getCache('previousDisplay')));
        }
    }
    
    public static function postSaveChild($_eqLogic) {
    }
		
	public static function convertHtml($_eqLogic,$_version = 'dashboard') {
	    
	    $replace = $_eqLogic->preToHtml($_version);
	    if (!is_array($replace)) {
	        return $replace;
	    }
	    $version = jeedom::versionAlias($_version);
	    foreach ($_eqLogic->getCmd() as $cmd) {
	        if ($cmd->getType() == 'info') {
	            $replace['#' . $cmd->getLogicalId() . '_history#'] = '';
	            $replace['#' . $cmd->getLogicalId() . '#'] = $cmd->execCmd();
	            $replace['#' . $cmd->getLogicalId() . '_state#'] = $cmd->execCmd();
	            $replace['#' . $cmd->getLogicalId() . '_id#'] = $cmd->getId();
	            $replace['#' . $cmd->getLogicalId() . '_uid#'] = 'cmd' . $cmd->getId() . self::UIDDELIMITER . mt_rand() . self::UIDDELIMITER;
	            $replace['#' . $cmd->getLogicalId() . '_collectDate#'] = $cmd->getCollectDate();
	            $replace['#' . $cmd->getLogicalId() . '_valueDate#'] = $cmd->getValueDate();
	            $replace['#' . $cmd->getLogicalId() . '_alertLevel#'] = $cmd->getCache('alertLevel');
	            if ($cmd->getIsHistorized() == 1) {
	                $replace['#' . $cmd->getLogicalId() . '_history#'] = 'history cursor';
	            }
	        } else {
	            $replace['#' . $cmd->getLogicalId() . '_id#'] = $cmd->getId();
	            $replace['#' . $cmd->getLogicalId() . '_uid#'] = 'cmd' . $cmd->getId() . self::UIDDELIMITER . mt_rand() . self::UIDDELIMITER;
	            $replace['#' . $cmd->getLogicalId() . '_state#'] = $cmd->getIsVisible();
	        }
	        
	        $replace['#' . $cmd->getLogicalId() . '_hide_name#'] = ($cmd->getDisplay('showNameOn' . $_version, 1) == 0 ? 'hidden' : ''); 
	        
	        if(is_array($cmd->getDisplay('parameters')) && count($cmd->getDisplay('parameters')) > 0){
	            foreach ($cmd->getDisplay('parameters') as $key => $value) {
	                $replace['#'.$cmd->getLogicalId().'_'.$key.'#'] = $value;
	            }
	        }
	    }
	    $refresh = $_eqLogic->getCmd(null, 'refresh');
	    $replace['#refresh#'] = is_object($refresh) ? $refresh->getId() : '';
	    
	    $replace['#enableautoSpray#'] = $_eqLogic->getCmd(null, 'autoSpray')->getConfiguration('enableautoSpray', 0);
	    
	    return $_eqLogic->postToHtml($_version, template_replace($replace, getTemplate('core', $version, $_eqLogic->getConfiguration('device'), 'blea')));
	    
	}
	
	public static function calculateOutputValue($_eqLogic,$_datas) {
	}
	
	public static function calculateInputValue($_eqLogic,$_datas) {
	    return $_datas;
	}

}

?>
