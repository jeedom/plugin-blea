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
<a class="btn btn-success btn-sm pull-right" id="bt_saveUser"><i class="fa fa-check-circle"></i> {{Sauvegarder}}</a>
<a class="btn btn-warning btn-sm userAction pull-right" data-action="add"><i class="fa fa-plus-circle"></i> {{Ajouter un utilisateur}}</a><br/><br/>
<table class="table table-condensed tablesorter" id="table_userList">
	<thead>
		<tr>
			<th>{{Surnom}}</th>
			<th>{{Taille}}</th>
			<th>{{Poids}}</th>
			<th>{{Action}}</th>
		</tr>
	</thead>
	<tbody>
	 <?php
foreach ($listUsers as $id => $data) {
	echo '<tr class="users"><td class="name"><input type="text" class="form-control" value="'.$data['name'].'" readonly/></td>';
	echo '<td class="height"><input type="text" class="form-control" value="'.$data['height'].'"/></td>';
	echo '<td class="weight"><input type="text" class="form-control" value="'.$data['weight'].'"/></td><td><a class="btn btn-danger btn-sm pull-right" id="bt_delUser"><i class="fa fa-times"></i></a></td></tr>';
	}
?>
	</tbody>
</table>
<script>
$('.userAction[data-action=add]').off('click').on('click', function () {
    addCmdToTable();
    $('.cmd:last .cmdAttr[data-l1key=type]').trigger('change');
});
function addCmdToTable(_cmd) {
    if (!isset(_cmd)) {
        var _cmd = {configuration: {}};
    }
    var tr = '<tr class="users"><td class="name"><input type="text" class="form-control" value=""/></td>';
    tr += '<td class="height"><input type="text" class="form-control" value=""/></td>';
    tr += '<td class="weight"><input type="text" class="form-control" value=""/></td>';
	tr += '<td><a class="btn btn-danger btn-sm pull-right" id="bt_delUser"><i class="fa fa-times"></i></a></td>';
    tr += '</tr>';
    $('#table_userList tbody').append(tr);
}
$('#bt_saveUser').on('click', function () {
    var userList= {}
	$('.users').each(function( index ) {
		data ={}
		name = $(this).find("td.name").find("input").value();
		height = $(this).find("td.height").find("input").value();
		weight = $(this).find("td.weight").find("input").value();
		data['name']= name;
		data['height']= height;
		data['weight'] = weight;
		userList[name] =data;
	});
	saveUserList(userList);
});

$('body').undelegate('#bt_delUser', 'click').delegate('#bt_delUser', 'click', function () {
  $(this).closest('tr').remove();
});

function saveUserList(userList) {
        $.ajax({// fonction permettant de faire de l'ajax
            type: "POST", // méthode de transmission des données au fichier php
            url: "plugins/blea/core/config/devices/miscale/ajax/miscale.ajax.php", // url du fichier php
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
            $('.ListUserDisplay').showAlert({message: data.result, level: 'danger'});
            return;
        }
		$('.ListUserDisplay').showAlert({message: 'Liste sauvegardée avec succès', level: 'success'});
        }
    });
}
</script>
