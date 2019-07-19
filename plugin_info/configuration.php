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

require_once dirname(__FILE__) . '/../../../core/php/core.inc.php';
include_file('core', 'authentification', 'php');
if (!isConnect('admin')) {
	throw new Exception('{{401 - Accès non autorisé}}');
}
?>
<form class="form-horizontal">
    <fieldset>
         <legend><i class="fa fa-list-alt"></i> {{Général}}</legend>
      <div class="form-group">
        <label class="col-lg-4 control-label">{{Autoriser l'inclusion de devices inconnus}}</label>
        <div class="col-lg-3">
           <input type="checkbox" class="configKey" data-l1key="allowAllinclusion" />
       </div>
	</div>
	 <div class="form-group">
        <label class="col-lg-4 control-label">{{Pas de local}}</label>
        <div class="col-lg-3">
           <input type="checkbox" class="configKey" data-l1key="noLocal" />
       </div>
	</div>
	
   </fieldset>
</form>
<form class="form-horizontal">
    <fieldset>
    <legend><i class="icon loisir-darth"></i> {{Démon}}</legend>
		 <div class="form-group">
	<label class="col-lg-4"></label>
	<div class="col-lg-8">
		<a class="btn btn-warning changeLogLive" data-log="logdebug"><i class="fa fa-cogs"></i> {{Mode debug forcé temporaire}}</a>
		<a class="btn btn-success changeLogLive" data-log="lognormal"><i class="fa fa-paperclip"></i> {{Remettre niveau de log local}}</a>
	</div>
	</br>
	</br>
	<label class="col-lg-4"></label>
	<div class="col-lg-8">
		<a class="btn btn-warning allantennas" data-action="update"><i class="fas fa-arrow-up"></i> {{Mettre à jour toutes les antennes}}</a>
		<a class="btn btn-success allantennas" data-action="restart"><i class="fas fa-play"></i> {{Redémarrer toutes les antennes}}</a>
	</div>
	</div>
       <div class="form-group">
        <label class="col-sm-4 control-label">{{Port clef bluetooth}}</label>
        <div class="col-sm-2">
            <select class="configKey form-control" data-l1key="port">
                <option value="none">{{Aucun}}</option>
                <?php
foreach (jeedom::getBluetoothMapping() as $name => $value) {
	echo '<option value="' . $name . '">' . $name . ' (' . $value . ')</option>';
}
?>
           </select>
       </div>
   </div>
   <div class="form-group">
    <label class="col-lg-4 control-label" data-help="{{Intervalle de scan présence. Il est déconseillé de descendre en dessous de 20 secondes}}">{{Intervalle de scan (s)}}</label>
    <div class="col-lg-2">
        <input class="configKey form-control" data-l1key="scaninterval" placeholder="{{20}}" />
    </div>
</div>
	<div class="form-group">
    <label class="col-lg-4 control-label" data-help="{{Combien de fois le device ne doit pas etre vu lors d'un scan pour décider qu'il est absent (fortement déconseillé de descendre en dessous de 3 ou 4 pour éviter les faux positifs}}">{{Nombre de scan invisible pour déclencher absence}}</label>
    <div class="col-lg-2">
        <input class="configKey form-control" data-l1key="absentnumber" placeholder="{{4}}" />
    </div>
</div>
   <div class="form-group">
    <label class="col-lg-4 control-label">{{Port socket interne (modification dangereuse)}}</label>
    <div class="col-lg-2">
        <input class="configKey form-control" data-l1key="socketport" placeholder="{{55008}}" />
    </div>
</div>
</fieldset>
</form>
<script>
 $('.changeLogLive').on('click', function () {
	 $.ajax({// fonction permettant de faire de l'ajax
            type: "POST", // methode de transmission des données au fichier php
            url: "plugins/blea/core/ajax/blea.ajax.php", // url du fichier php
            data: {
                action: "changeLogLive",
				level : $(this).attr('data-log')
            },
            dataType: 'json',
            error: function (request, status, error) {
                handleAjaxError(request, status, error);
            },
            success: function (data) { // si l'appel a bien fonctionné
                if (data.state != 'ok') {
                    $('#div_alert').showAlert({message: data.result, level: 'danger'});
                    return;
                }
                $('#div_alert').showAlert({message: '{{Réussie}}', level: 'success'});
            }
        });
});

$('.allantennas').on('click', function () {
	if ($(this).attr('data-action') == 'update') {
		action = 'sendremotes';
	} else {
		action = 'launchremotes';
	}
	console.log(action);
	 $.ajax({// fonction permettant de faire de l'ajax
            type: "POST", // methode de transmission des données au fichier php
            url: "plugins/blea/core/ajax/blea.ajax.php", // url du fichier php
            data: {
                action: action
            },
            dataType: 'json',
            error: function (request, status, error) {
                handleAjaxError(request, status, error);
            },
            success: function (data) { // si l'appel a bien fonctionné
                if (data.state != 'ok') {
                    $('#div_alert').showAlert({message: data.result, level: 'danger'});
                    return;
                }
                $('#div_alert').showAlert({message: '{{Réussie}}', level: 'success'});
            }
        });
});
function blea_postSaveConfiguration(){
  $.ajax({
    type: "POST",
    url: "plugins/blea/core/ajax/blea.ajax.php",
    data: {
      action: "launchremotes",
    },
    dataType: 'json',
    global: false,
    error: function (request, status, error) {
      handleAjaxError(request, status, error);
    },
    success: function (data) {
      if (data.state != 'ok') {
        $('#div_alert').showAlert({message: data.result, level: 'danger'});
        return;
      }
    }
  });
}
</script>
