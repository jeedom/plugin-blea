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
?>
<div id='div_bleaRemoteAlert' style="display: none;"></div>
<div class="row row-overflow">
	<div class="col-lg-3 col-md-4 col-sm-5 col-xs-5">
		<div class="bs-sidebar">
			<ul id="ul_eqLogic" class="nav nav-list bs-sidenav">
				<a class="btn btn-default bleaRemoteAction" style="width : 100%;margin-top : 5px;margin-bottom: 5px;" data-action="add"><i class="fa fa-plus-circle"></i> {{Ajouter une Antenne Bluetooth}}</a>
				<li class="filter" style="margin-bottom: 5px;"><input class="filter form-control input-sm" placeholder="{{Rechercher}}" style="width: 100%"/></li>
				<?php
foreach ($remotes as $remote) {
	echo '<li class="cursor li_bleaRemote" data-bleaRemote_id="' . $remote->getId() . '"><a>' . $remote->getName() . '</a></li>';
}
?>
			</ul>
		</div>
	</div>

	<div class="col-lg-9 col-md-8 col-sm-7 col-xs-7 bleaRemote" style="border-left: solid 1px #EEE; padding-left: 25px;display:none;">
		<a class="btn btn-success bleaRemoteAction pull-right" data-action="save"><i class="fa fa-check-circle"></i> {{Sauvegarder}}</a>
		<a class="btn btn-danger bleaRemoteAction pull-right" data-action="remove"><i class="fa fa-minus-circle"></i> {{Supprimer}}</a>

			<form class="form-horizontal">
					<fieldset>
						<legend>{{Général}}</legend>
						<div class="form-group">
							<label class="col-sm-3 control-label">{{Nom de l'antenne}}</label>
							<div class="col-sm-3">
								<input type="text" class="bleaRemoteAttr form-control" data-l1key="id" style="display : none;" />
								<input type="text" class="bleaRemoteAttr form-control" data-l1key="remoteName" placeholder="{{Nom de l'antenne}}"/>
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-3 control-label">{{Ip}}</label>
							<div class="col-sm-3">
								<input type="text" class="bleaRemoteAttr form-control" data-l1key="configuration" data-l2key="remoteIp"/>
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-3 control-label">{{Port}}</label>
							<div class="col-sm-3">
								<input type="text" class="bleaRemoteAttr form-control" data-l1key="configuration" data-l2key="remotePort"/>
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-3 control-label">{{User}}</label>
							<div class="col-sm-3">
								<input type="text" class="bleaRemoteAttr form-control" data-l1key="configuration" data-l2key="remoteUser"/>
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-3 control-label">{{Password}}</label>
							<div class="col-sm-3">
								<input type="text" class="bleaRemoteAttr form-control" data-l1key="configuration" data-l2key="remotePassword"/>
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-3 control-label">{{Device}}</label>
							<div class="col-sm-3">
								<input type="text" class="bleaRemoteAttr form-control" data-l1key="configuration" data-l2key="remoteDevice" placeholder="{{ex : hci0}}"/>
							</div>
						</div>
					</fieldset>
				</form>
	</div>
</div>


<script>
	$('.bleaRemoteAction[data-action=add]').on('click',function(){
		$('.bleaRemote').show();
		$('.bleaRemoteAttr').value('');
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
			error: function (request, status, error) {
				handleAjaxError(request, status, error,$('#div_bleaRemoteAlert'));
			},
			success: function (data) {
				if (data.state != 'ok') {
					$('#div_bleaRemoteAlert').showAlert({message: data.result, level: 'danger'});
					return;
				}
				$('.bleaRemote').show();
				$('.bleaRemoteAttr').value('');
				$('.bleaRemote').setValues(data.result,'.bleaRemoteAttr');
			}
		});
	}

	$('.li_bleaRemote').on('click',function(){
		displaybleaRemote($(this).attr('data-bleaRemote_id'));
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
				displaybleaRemote(data.result.id);
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
					}
				});
			}
		});
	});
</script>