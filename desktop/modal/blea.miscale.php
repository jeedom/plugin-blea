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

if (!isConnect('admin')) {
	throw new Exception('{{401 - Accès non autorisé}}');
}
if (init('id') == '') {
	throw new Exception('{{EqLogic ID ne peut être vide}}');
}
$eqLogic = eqLogic::byId(init('id'));
if (!is_object($eqLogic)) {
	throw new Exception('{{EqLogic non trouvé}}');
}
sendVarToJS('configureDeviceId', init('id'));
$listUsers = $eqLogic->getConfiguration('userList',array());
?>
<div class="ListUserDisplay"></div>
<a class="btn btn-success pull-right" id="bt_saveUser"><i class="fa fa-check-circle"></i> {{Sauvegarder}}</a>
<table class="table table-condensed tablesorter" id="table_userList">
	<thead>
		<tr>
			<th>{{Surnom}}</th>
			<th>{{Taille}}</th>
			<th>{{Poids}}</th>
		</tr>
	</thead>
	<tbody>
	 <?php
foreach ($listUsers as $id => $data) {
	echo '<tr><td><input type="text" class="form-control" value="'.$data['name'].'"/></td>';
	echo '<tr><td><input type="text" class="form-control" value="'.$data['size'].'"/></td>';
	echo '<tr><td><input type="text" class="form-control" value="'.$data['weight'].'"/></td>';
	}
?>
	</tbody>
</table>
<script>
$('#bt_saveUser').on('click', function () {
    var userList= {}
	$('.username').each(function( index ) {
		userList[$(this).attr('data-id')] ='{"name" :"' + $(this).value()+'","type" : "'+$(this).attr('data-type')+'"}';
	});
	saveUserList(userList);
});

function saveUserList(userList) {
        $.ajax({// fonction permettant de faire de l'ajax
            type: "POST", // méthode de transmission des données au fichier php
            url: "plugins/avidsen/core/ajax/avidsen.ajax.php", // url du fichier php
            data: {
                action: "saveUserList",
				id : configureDeviceId,
                userList: json_encode(userList)
            },
            dataType: 'json',
            error: function (request, status, error) {
            handleAjaxError(request, status, error);
        },
        success: function (data) { // si l'appel a bien fonctionné
        if (data.state != 'ok') {
            $('.EnregistrementDisplay').showAlert({message: data.result, level: 'danger'});
            return;
        }
		$('.EnregistrementDisplay').showAlert({message: 'Liste sauvegardée avec succès', level: 'success'});
        }
    });
}
</script>
