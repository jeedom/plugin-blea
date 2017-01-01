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

$remotes = blea_remote::all();
$id = init('id');
sendVarToJS('plugin', $id);
?>
<div id='div_bleaRemoteAlert' style="display: none;"></div>
<div class="row row-overflow">
	<div class="col-lg-2 col-md-3 col-sm-4 col-xs-4">
		<div class="bs-sidebar">
			<ul id="ul_eqLogic" class="nav nav-list bs-sidenav">
				<a class="btn btn-default bleaRemoteAction" style="width : 100%;margin-top : 5px;margin-bottom: 5px;" data-action="add"><i class="fa fa-plus-circle"></i> {{Ajouter Antenne}}</a>
				<li class="filter" style="margin-bottom: 5px;"><input class="filter form-control input-sm" placeholder="{{Rechercher}}" style="width: 100%"/></li>
				<?php
foreach ($remotes as $remote) {
	$icon = '<i class="fa fa-heartbeat" style="color:green"></i>';
	$last = $remote->getConfiguration('lastupdate','0');
	if ($last == '0' or time() - strtotime($last)>65){
		$icon = '<i class="fa fa-deaf" style="color:#b20000"></i>';
	}
	echo '<li class="cursor li_bleaRemote" data-bleaRemote_id="' . $remote->getId() . '" data-bleaRemote_name="' . $remote->getRemoteName() . '"><a>' . $remote->getRemoteName() . ' '. $icon.'</a></li>';
}
?>
			</ul>
		</div>
	</div>
	 <div class="col-lg-10 col-md-9 col-sm-8 col-xs-8 remoteThumbnailDisplay" style="border-left: solid 1px #EEE; padding-left: 25px;">
<legend><i class="fa fa-table"></i>  {{Mes Antennes}}</legend>

<div class="eqLogicThumbnailContainer">
	<div class="cursor bleaRemoteAction pull-left" data-action="add" style="background-color : #ffffff; height : 140px;margin-bottom : 10px;padding : 5px;border-radius: 2px;width : 160px;margin-left : 10px;" >
     <center>
      <i class="fa fa-plus-circle" style="font-size : 9em;color:#94ca02;"></i>
    </center>
    <span style="font-size : 1.1em;position:relative; top : 15px;word-break: break-all;white-space: pre-wrap;word-wrap: break-word;color:#94ca02"><center>{{Ajouter}}</center></span>
  </div>
  <?php
foreach ($remotes as $remote) {
	echo '<div class="eqLogicDisplayCard cursor pull-left" data-remote_id="' . $remote->getId() . '" style="background-color : #ffffff; height : 140px;margin-bottom : 10px;padding : 5px;border-radius: 2px;width : 160px;margin-left : 10px;" >';
	echo "<center>";
	echo '<img class="lazy" src="plugins/blea/3rdparty/antenna.png" height="105" width="95" />';
	echo "</center>";
	echo '<span style="font-size : 1.1em;position:relative; top : 15px;word-break: break-all;white-space: pre-wrap;word-wrap: break-word;color:#94ca02""><center>' . $remote->getRemoteName() . '</center></span>';
	echo '</div>';
}
?>
</div>
</div>

	<div class="col-lg-10 col-md-9 col-sm-8 col-xs-8 bleaRemote" style="border-left: solid 1px #EEE; padding-left: 25px;display:none;">
		<a class="btn btn-success bleaRemoteAction pull-right" data-action="save"><i class="fa fa-check-circle"></i> {{Sauvegarder}}</a>
		<a class="btn btn-danger bleaRemoteAction pull-right" data-action="remove"><i class="fa fa-minus-circle"></i> {{Supprimer}}</a>

			<form class="form-horizontal">
					<fieldset>
						<legend><i class="fa fa-arrow-circle-left returnAction cursor"></i> {{Général}}</legend>
						<div class="form-group">
							<label class="col-sm-2 control-label">{{Nom}}</label>
							<div class="col-sm-3">
								<input type="text" class="bleaRemoteAttr form-control" data-l1key="id" style="display : none;" />
								<input type="text" class="bleaRemoteAttr form-control" data-l1key="remoteName" placeholder="{{Nom de l'antenne}}"/>
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-2 control-label">{{Ip}}</label>
							<div class="col-sm-3">
								<input type="text" class="bleaRemoteAttr form-control" data-l1key="configuration" data-l2key="remoteIp"/>
							</div>
							<label class="col-sm-1 control-label">{{Port}}</label>
							<div class="col-sm-3">
								<input type="text" class="bleaRemoteAttr form-control" data-l1key="configuration" data-l2key="remotePort"/>
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-2 control-label">{{User}}</label>
							<div class="col-sm-3">
								<input type="text" class="bleaRemoteAttr form-control" data-l1key="configuration" data-l2key="remoteUser"/>
							</div>
							<label class="col-sm-1 control-label">{{Password}}</label>
							<div class="col-sm-3">
								<input type="password" class="bleaRemoteAttr form-control" data-l1key="configuration" data-l2key="remotePassword"/>
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-2 control-label">{{Device}}</label>
							<div class="col-sm-3">
								<input type="text" class="bleaRemoteAttr form-control" data-l1key="configuration" data-l2key="remoteDevice" placeholder="{{ex : hci0}}"/>
							</div>
						</div>
						<div class="form-group expertModeVisible">
							<label class="col-sm-2 control-label">{{Communication}}</label>
							<div class="col-sm-3">
								<span class="bleaRemoteAttr bleaRemoteAttrcomm label label-default" data-l1key="configuration" data-l2key="lastupdate" title="{{Date de dernière communication}}" style="font-size : 1em;cursor : default;"></span>
							</div>
						</div>
						<?php
						if (method_exists( $id ,'sendRemoteFiles')){
							echo '<div class="form-group">
						<label class="col-sm-2 control-label">{{Envoie des fichiers nécessaires}}</label>
						<div class="col-sm-3">
							<a class="btn btn-warning bleaRemoteAction" data-action="sendFiles"><i class="fa fa-upload"></i> {{Envoyer les fichiers}}</a>
						</div>';
						if (method_exists( $id ,'dependancyRemote')){
							echo '<label class="col-sm-2 control-label">{{Installation des dépendances}}</label>
						<div class="col-sm-3">
							<a class="btn btn-warning bleaRemoteAction" data-action="dependancyRemote"><i class="fa fa-spinner"></i> {{Lancer les dépendances}}</a>
						</div>
						<div class="col-sm-2">
							<a class="btn btn-success bleaRemoteAction" data-action="getRemoteLogDependancy"><i class="fa fa-file-text-o"></i> {{Log dépendances}}</a>
						</div>';
						}
						echo'</div>';
						}
						if (method_exists( $id ,'launchremote')){
							echo '<div class="form-group">
						<label class="col-sm-2 control-label">{{Gestion du démon}}</label>
						<div class="col-sm-2">
							<a class="btn btn-success bleaRemoteAction" data-action="launchremote"><i class="fa fa-play"></i> {{Lancer}}</a>
						</div>
						<div class="col-sm-2">
							<a class="btn btn-danger bleaRemoteAction" data-action="stopremote"><i class="fa fa-stop"></i> {{Arret}}</a>
						</div>
						<div class="col-sm-2">
							<a class="btn btn-success bleaRemoteAction" data-action="getRemoteLog"><i class="fa fa-file-text-o"></i> {{Log}}</a>
						</div>
						</div>';
						}
						if (method_exists( $id ,'remotelearn')){
							echo '<div class="form-group">
						<label class="col-sm-2 control-label">{{Mettre en learn}}</label>
						<div class="col-sm-2">
							<a class="btn btn-success bleaRemoteAction" data-action="remotelearn" data-type="1"><i class="fa fa-sign-in fa-rotate-90"></i> {{Inclusion}}</a>
						</div>
						<label class="col-sm-2 control-label">{{Arrêter learn}}</label>
						<div class="col-sm-2">
							<a class="btn btn-danger bleaRemoteAction" data-action="remotelearn" data-type="0"><i class="fa fa-sign-in fa-rotate-270"></i> {{Stop Inclusion}}</a>
						</div>
						</div>';
						}
						?>
						</fieldset>
				</form>
	</div>
</div>

<script>
	$('.bleaRemoteAction[data-action=add]').on('click',function(){
		$('.bleaRemote').show();
		$('.remoteThumbnailDisplay').hide();
		$('.bleaRemoteAttr').value('');
	});
	
	$('.eqLogicDisplayCard').on('click',function(){
		displaybleaRemote($(this).attr('data-remote_id'));
	});

	function displaybleaRemote(_id){
		$('.li_bleaRemote').removeClass('active');
		$('.li_bleaRemote[data-bleaRemote_id='+_id+']').addClass('active');
		$.ajax({
			type: "POST",
			url: "plugins/blea/core/ajax/blea.ajax.php",
			data: {
				action: "get_bleaRemote",
				id: _id,
			},
			dataType: 'json',
			async: true,
			global: false,
			error: function (request, status, error) {
			},
			success: function (data) {
				if (data.state != 'ok') {
					return;
				}
				$('.bleaRemote').show();
				$('.remoteThumbnailDisplay').hide();
				$('.bleaRemoteAttr').value('');
				$('.bleaRemote').setValues(data.result,'.bleaRemoteAttr');
			}
		});
	}
	
	function displaybleaRemoteComm(_id){
		$('.li_bleaRemote').removeClass('active');
		$('.li_bleaRemote[data-bleaRemote_id='+_id+']').addClass('active');
		$.ajax({
			type: "POST",
			url: "plugins/blea/core/ajax/blea.ajax.php",
			data: {
				action: "get_bleaRemote",
				id: _id,
			},
			dataType: 'json',
			async: true,
			global: false,
			error: function (request, status, error) {
			},
			success: function (data) {
				if (data.state != 'ok') {
					return;
				}
				$('.bleaRemote').show();
				$('.bleaRemoteAttrcomm').value('');
				$('.bleaRemote').setValues(data.result,'.bleaRemoteAttrcomm');
			}
		});
	}

	$('.li_bleaRemote').on('click',function(){
		displaybleaRemote($(this).attr('data-bleaRemote_id'));
		$('.remoteThumbnailDisplay').hide();
	});
	
	$('.returnAction').on('click',function(){
		$('.bleaRemote').hide();
		$('.li_bleaRemote').removeClass('active');
		setTimeout(function() { $('.remoteThumbnailDisplay').show() }, 100);
		;
	});

	$('.bleaRemoteAction[data-action=save]').on('click',function(){
		var blea_remote = $('.bleaRemote').getValues('.bleaRemoteAttr')[0];
		$.ajax({
			type: "POST",
			url: "plugins/blea/core/ajax/blea.ajax.php",
			data: {
				action: "save_bleaRemote",
				blea_remote: json_encode(blea_remote),
			},
			dataType: 'json',
			error: function (request, status, error) {
				handleAjaxError(request, status, error,$('#div_bleaRemoteAlert'));
			},
			success: function (data) {
				if (data.state != 'ok') {
					$('#div_bleaRemoteAlert').showAlert({message: data.result, level: 'danger'});
					return;
				}
				$('#div_bleaRemoteAlert').showAlert({message: '{{Sauvegarde réussie}}', level: 'success'});
				$('#md_modal').dialog('close');
				$('#md_modal').dialog({title: "{{Gestion des antennes bluetooth}}"});
				$('#md_modal').load('index.php?v=d&plugin=blea&modal=blea.remote&id=blea').dialog('open');
				setTimeout(function() { displaybleaRemote(data.result.id) }, 200);
				
			}
		});
	});
	
	$('.bleaRemoteAction[data-action=sendFiles]').on('click',function(){
		var blea_remote = $('.bleaRemote').getValues('.bleaRemoteAttr')[0];
		$.ajax({
			type: "POST",
			url: "plugins/"+plugin+"/core/ajax/"+plugin+".ajax.php",
			data: {
				action: "sendRemoteFiles",
				remoteId: $('.li_bleaRemote.active').attr('data-bleaRemote_id'),
			},
			dataType: 'json',
			error: function (request, status, error) {
				handleAjaxError(request, status, error,$('#div_bleaRemoteAlert'));
			},
			success: function (data) {
				if (data.state != 'ok') {
					$('#div_bleaRemoteAlert').showAlert({message: data.result, level: 'danger'});
					return;
				}
				$('#div_bleaRemoteAlert').showAlert({message: '{{Envoie réussie}}', level: 'success'});
			}
		});
	});
	
	$('.bleaRemoteAction[data-action=getRemoteLog]').on('click',function(){
		var blea_remote = $('.bleaRemote').getValues('.bleaRemoteAttr')[0];
		$.ajax({
			type: "POST",
			url: "plugins/"+plugin+"/core/ajax/"+plugin+".ajax.php",
			data: {
				action: "getRemoteLog",
				remoteId: $('.li_bleaRemote.active').attr('data-bleaRemote_id'),
			},
			dataType: 'json',
			error: function (request, status, error) {
				handleAjaxError(request, status, error,$('#div_bleaRemoteAlert'));
			},
			success: function (data) {
				if (data.state != 'ok') {
					$('#div_bleaRemoteAlert').showAlert({message: data.result, level: 'danger'});
					return;
				}
				$('#div_bleaRemoteAlert').showAlert({message: '{{Log récupérée}}', level: 'success'});
			}
		});
	});
	
	$('.bleaRemoteAction[data-action=getRemoteLogDependancy]').on('click',function(){
		var blea_remote = $('.bleaRemote').getValues('.bleaRemoteAttr')[0];
		$.ajax({
			type: "POST",
			url: "plugins/"+plugin+"/core/ajax/"+plugin+".ajax.php",
			data: {
				action: "getRemoteLogDependancy",
				remoteId: $('.li_bleaRemote.active').attr('data-bleaRemote_id'),
			},
			dataType: 'json',
			error: function (request, status, error) {
				handleAjaxError(request, status, error,$('#div_bleaRemoteAlert'));
			},
			success: function (data) {
				if (data.state != 'ok') {
					$('#div_bleaRemoteAlert').showAlert({message: data.result, level: 'danger'});
					return;
				}
				$('#div_bleaRemoteAlert').showAlert({message: '{{Log récupérée}}', level: 'success'});
			}
		});
	});
	
	$('.bleaRemoteAction[data-action=launchremote]').on('click',function(){
		var blea_remote = $('.bleaRemote').getValues('.bleaRemoteAttr')[0];
		$.ajax({
			type: "POST",
			url: "plugins/"+plugin+"/core/ajax/"+plugin+".ajax.php",
			data: {
				action: "launchremote",
				remoteId: $('.li_bleaRemote.active').attr('data-bleaRemote_id'),
			},
			dataType: 'json',
			error: function (request, status, error) {
				handleAjaxError(request, status, error,$('#div_bleaRemoteAlert'));
			},
			success: function (data) {
				if (data.state != 'ok') {
					$('#div_bleaRemoteAlert').showAlert({message: data.result, level: 'danger'});
					return;
				}
				$('#div_bleaRemoteAlert').showAlert({message: '{{Envoie réussie}}', level: 'success'});
			}
		});
	});
	
	$('.bleaRemoteAction[data-action=dependancyRemote]').on('click',function(){
		var blea_remote = $('.bleaRemote').getValues('.bleaRemoteAttr')[0];
		$.ajax({
			type: "POST",
			url: "plugins/"+plugin+"/core/ajax/"+plugin+".ajax.php",
			data: {
				action: "dependancyRemote",
				remoteId: $('.li_bleaRemote.active').attr('data-bleaRemote_id'),
			},
			dataType: 'json',
			error: function (request, status, error) {
				handleAjaxError(request, status, error,$('#div_bleaRemoteAlert'));
			},
			success: function (data) {
				if (data.state != 'ok') {
					$('#div_bleaRemoteAlert').showAlert({message: data.result, level: 'danger'});
					return;
				}
				$('#div_bleaRemoteAlert').showAlert({message: '{{Envoie réussie}}', level: 'success'});
			}
		});
	});
	
	$('.bleaRemoteAction[data-action=stopremote]').on('click',function(){
		var blea_remote = $('.bleaRemote').getValues('.bleaRemoteAttr')[0];
		$.ajax({
			type: "POST",
			url: "plugins/"+plugin+"/core/ajax/"+plugin+".ajax.php",
			data: {
				action: "stopremote",
				remoteId: $('.li_bleaRemote.active').attr('data-bleaRemote_id'),
			},
			dataType: 'json',
			error: function (request, status, error) {
				handleAjaxError(request, status, error,$('#div_bleaRemoteAlert'));
			},
			success: function (data) {
				if (data.state != 'ok') {
					$('#div_bleaRemoteAlert').showAlert({message: data.result, level: 'danger'});
					return;
				}
				$('#div_bleaRemoteAlert').showAlert({message: '{{Envoie réussie}}', level: 'success'});
			}
		});
	});
	
	$('.bleaRemoteAction[data-action=remotelearn]').on('click',function(){
		var blea_remote = $('.bleaRemote').getValues('.bleaRemoteAttr')[0];
		$.ajax({
			type: "POST",
			url: "plugins/"+plugin+"/core/ajax/"+plugin+".ajax.php",
			data: {
				action: "remotelearn",
				remoteId: $('.li_bleaRemote.active').attr('data-bleaRemote_id'),
				state: $(this).attr('data-type'),
			},
			dataType: 'json',
			error: function (request, status, error) {
				handleAjaxError(request, status, error,$('#div_bleaRemoteAlert'));
			},
			success: function (data) {
				if (data.state != 'ok') {
					$('#div_bleaRemoteAlert').showAlert({message: data.result, level: 'danger'});
					return;
				}
				$('#div_bleaRemoteAlert').showAlert({message: '{{Envoie réussie}}', level: 'success'});
			}
		});
	});

	$('.bleaRemoteAction[data-action=remove]').on('click',function(){
		bootbox.confirm('{{Etês-vous sûr de vouloir supprimer cette Antenne ?}}', function (result) {
			if (result) {
				$.ajax({
					type: "POST",
					url: "plugins/blea/core/ajax/blea.ajax.php",
					data: {
						action: "remove_bleaRemote",
						id: $('.li_bleaRemote.active').attr('data-bleaRemote_id'),
					},
					dataType: 'json',
					error: function (request, status, error) {
						handleAjaxError(request, status, error,$('#div_bleaRemoteAlert'));
					},
					success: function (data) {
						if (data.state != 'ok') {
							$('#div_bleaRemoteAlert').showAlert({message: data.result, level: 'danger'});
							return;
						}
						$('.li_bleaRemote.active').remove();
						$('.bleaRemote').hide();
						$('.remoteThumbnailDisplay').show();
						$('#md_modal').dialog('close');
						$('#md_modal').dialog({title: "{{Gestion des antennes bluetooth}}"});
						$('#md_modal').load('index.php?v=d&plugin=blea&modal=blea.remote&id=blea').dialog('open');
					}
				});
			}
		});
	});
window.setInterval(function () {
    displaybleaRemoteComm($('.li_bleaRemote.active').attr('data-bleaRemote_id'));
}, 5000);
</script>