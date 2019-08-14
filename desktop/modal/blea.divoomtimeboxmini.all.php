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
	throw new Exception('401 Unauthorized');
}
echo '<div class="row" style="height:100%; width: 100%">';
echo '<div class="eventDisplayMini"></div>';
echo '<div class="col-lg-12">';
$file = dirname(__FILE__) . '/../../data/collection_divoomtimeboxmini.json';
$dataMemory = array();
if (file_exists($file)) {
	$dataMemory = json_decode(file_get_contents($file), true);
}
echo'<div class="form-group pull-right">
			<span class="btn btn-success btn-file" style="width:100%;" title="Uploader un fichier">
								<i class="fas fa-upload"></i><input id="bt_uploadFile" type="file" name="file" data-url="plugins/blea/core/config/devices/divoomtimeboxmini/ajax/divoomtimeboxmini.ajax.php?action=fileupload">
							</span>
		</div>
<a class="btn btn-warning bt_syncimages pull-right" title="Envoyer les fichiers images sur les antennes"><i class="fas fa-retweet"></i></a></br></br>';
foreach ($dataMemory as $name=>$data){

echo '<div class="form-group pull-left" style="overflow:hidden;height:10em">';
echo '<div class="miniImageName" data-name="' . $name .'"><span class="label label-info" style="font-size:1em;cursor:default">' . ucfirst($name) . '</span>
<a class="btn btn-xs btn-success bt_renameImageMini"><i class="fas fa-retweet"></i></a>
<a class="btn btn-xs btn-warning bt_loadImageMini"><i class="fas fa-download"></i></a>
<a class="btn btn-xs btn-danger bt_delImageMini"><i class="fas fa-trash"></i></a></div>';
$i = 1;
$line = 0;
while ($i < 122) {
	$j = 1;
	while ($j < 12) {
		$marginTop = '0px';
		if ($i >= 12){
			$marginTop = (-0.9*$line).'em';
		}
		echo '<label class="fa fa-stop" style="color : ' . $data[$i] . ';font-size:0.8em;vertical-align:top; margin-top:' . $marginTop . ';margin-left:-1px;cursor:default;border-radius:0"></label>';
		$j++;
		$i++;

	}
	if ($i != 122){
		echo '<br/>';
		$line+=1;
	}
}

echo '</div>';
}
$dir = dirname(__FILE__) . '/../../data/divoomtimeboxmini';
$files = array();
echo '<div class="col-lg-12">';
foreach (ls($dir, '*') as $file) {
	echo '<div class="form-group pull-left">';
	echo '<div class="miniImageName" data-name="' . $file .'"><span class="label label-info" style="font-size:1em;cursor:default">' . ucfirst($file) . '</span>
<a class="btn btn-xs btn-success bt_renameImageMiniFile"><i class="fas fa-retweet"></i></a>
<a class="btn btn-xs btn-danger bt_delImageMiniFile"><i class="fas fa-trash"></i></a></div>';
echo '<center><img class="" src="plugins/blea/data/divoomtimeboxmini/'.$file . '" height="33"/></center>';
echo '</div>';
}
echo '</div>';
echo '</div>';
echo '</div>';
?>
<script>
$('.bt_syncimages').on('click', function () {
		$.ajax({
				type: "POST",
				url: "plugins/blea/core/config/devices/divoomtimeboxmini/ajax/divoomtimeboxmini.ajax.php",
				data: {
					action: "sendFiles",
				},
							global : false,
							dataType: 'json',
							error: function(request, status, error) {
								handleAjaxError(request, status, error);
							},
							success: function(data) {
								if (data.state != 'ok') {
									$('.eventDisplayMini').showAlert({message:  data.result,level: 'danger'});
									setTimeout(function() { deleteAlertMini() }, 2000);
									return;
								}
								$('.eventDisplayMini').showAlert({message:  'Envoi effectué' ,level: 'success'});
								setTimeout(function() { deleteAlertMini() }, 2000);
								modifyWithoutSave=false;
							}
						});
	});
$('#bt_uploadFile').fileupload({
  dataType: 'json',
  replaceFileInput: false,
  done: function (e, data) {
    if (data.result.state != 'ok') {
      $('.eventDisplayMini').showAlert({message: data.result.result, level: 'danger'});
      return;
    }
   $('.eventDisplayMini').showAlert({message: '{{Fichier(s) ajouté(s) avec succès}}', level: 'success'});
   $('#md_modal2').dialog('close');
	$('#md_modal2').dialog({title: "{{Votre Collection}}"});
	$('#md_modal2').load('index.php?v=d&plugin=blea&modal=blea.divoomtimeboxmini.all').dialog('open');
  }
});
$('.bt_delImageMini').on('click', function () {
		var oriname = $(this).closest('.miniImageName').attr('data-name');
		bootbox.dialog({
			title: 'Etes-vous sur ?',
			message: 'Vous allez supprimer l\'image avec le nom "' + oriname.charAt(0).toUpperCase() + oriname.slice(1) +'" ! Voulez-vous continuer ?',
			buttons: {
				"{{Annuler}}": {
					className: "btn-danger",
					callback: function () {
					}
				},
				success: {
					label: "{{Continuer}}",
					className: "btn-success",
					callback: function () {
						$.ajax({
							type: "POST",
							url: "plugins/blea/core/config/devices/divoomtimeboxmini/ajax/divoomtimeboxmini.ajax.php",
							data: {
								action: "delImage",
								name: oriname
							},
							global : false,
							dataType: 'json',
							error: function(request, status, error) {
								handleAjaxError(request, status, error);
							},
							success: function(data) {
								if (data.state != 'ok') {
									$('.eventDisplayMini').showAlert({message:  data.result,level: 'danger'});
									setTimeout(function() { deleteAlertMini() }, 2000);
									return;
								}
								$('.eventDisplayMini').showAlert({message:  'Suppression effectuée' ,level: 'success'});
								setTimeout(function() { deleteAlertMini() }, 2000);
								modifyWithoutSave=false;
								$('#md_modal2').dialog('close');
								$('#md_modal2').dialog({title: "{{Votre Collection}}"});
								$('#md_modal2').load('index.php?v=d&plugin=blea&modal=blea.divoomtimeboxmini.all').dialog('open');
							}
						});
					}
				},
			}
		});
	});

	$('.bt_delImageMiniFile').on('click', function () {
		var oriname = $(this).closest('.miniImageName').attr('data-name');
		bootbox.dialog({
			title: 'Etes-vous sur ?',
			message: 'Vous allez supprimer l\'image avec le nom "' + oriname.charAt(0).toUpperCase() + oriname.slice(1) +'" ! Voulez-vous continuer ?',
			buttons: {
				"{{Annuler}}": {
					className: "btn-danger",
					callback: function () {
					}
				},
				success: {
					label: "{{Continuer}}",
					className: "btn-success",
					callback: function () {
						$.ajax({
							type: "POST",
							url: "plugins/blea/core/config/devices/divoomtimeboxmini/ajax/divoomtimeboxmini.ajax.php",
							data: {
								action: "delImageFile",
								name: oriname
							},
							global : false,
							dataType: 'json',
							error: function(request, status, error) {
								handleAjaxError(request, status, error);
							},
							success: function(data) {
								if (data.state != 'ok') {
									$('.eventDisplayMini').showAlert({message:  data.result,level: 'danger'});
									setTimeout(function() { deleteAlertMini() }, 2000);
									return;
								}
								$('.eventDisplayMini').showAlert({message:  'Suppression effectuée' ,level: 'success'});
								setTimeout(function() { deleteAlertMini() }, 2000);
								modifyWithoutSave=false;
								$('#md_modal2').dialog('close');
								$('#md_modal2').dialog({title: "{{Votre Collection}}"});
								$('#md_modal2').load('index.php?v=d&plugin=blea&modal=blea.divoomtimeboxmini.all').dialog('open');
							}
						});
					}
				},
			}
		});
	});

	$('.bt_loadImageMini').on('click', function () {
		var oriname = $(this).closest('.miniImageName').attr('data-name');
		$.ajax({
			type: "POST",
			url: "plugins/blea/core/config/devices/divoomtimeboxmini/ajax/divoomtimeboxmini.ajax.php",
			data: {
				action: "loadImage",
				name: oriname
			},
			dataType: 'json',
			global: false,
			error: function(request, status, error) {
				handleAjaxError(request, status, error);
			},
			success: function(data) {
				if (data.state != 'ok') {
					$('.eventDisplayMini').showAlert({message:  data.result,level: 'danger'});
					setTimeout(function() { deleteAlertMini() }, 2000);
					return;
				}
				$('.memoryload').value(oriname);
				$('#md_modal2').dialog('close');
				modifyWithoutSave=false;
			}
		});
	});

	$('.bt_renameImageMini').on('click', function () {
		var oriname = $(this).closest('.miniImageName').attr('data-name');
		var newname = prompt("Quel nouveau nom voulez-vous donner à l'image?", "")
		if (newname == ''){
			$('.eventDisplayMini').showAlert({message:  'Vous devez spécifier un nom pour sauver une image',level: 'danger'});
			setTimeout(function() { deleteAlertMini()}, 2000);
			return;
		}
		bootbox.dialog({
			title: 'Etes-vous sur ?',
			message: 'Vous allez renommer l\'image : "' + oriname.charAt(0).toUpperCase() + oriname.slice(1) + '" en : "' + newname.charAt(0).toUpperCase() + newname.slice(1) + '" ! Voulez-vous continuer ?',
			buttons: {
				"{{Annuler}}": {
					className: "btn-danger",
					callback: function () {
					}
				},
				success: {
					label: "{{Continuer}}",
					className: "btn-success",
					callback: function () {
						$.ajax({
							type: "POST",
							url: "plugins/blea/core/config/devices/divoomtimeboxmini/ajax/divoomtimeboxmini.ajax.php",
							data: {
								action: "renameImage",
								oriname: oriname,
								newname: newname

							},
							global : false,
							dataType: 'json',
							error: function(request, status, error) {
								handleAjaxError(request, status, error);
							},
							success: function(data) {
								if (data.state != 'ok') {
									$('.eventDisplayMini').showAlert({message:  data.result,level: 'danger'});
									setTimeout(function() { deleteAlertMini() }, 2000);
									return;
								}
								$('.eventDisplayMini').showAlert({message:  'Renommage effectué' ,level: 'success'});
								setTimeout(function() { deleteAlertMini() }, 2000);
								$('#md_modal2').dialog('close');
								$('#md_modal2').dialog({title: "{{Votre Collection}}"});
								$('#md_modal2').load('index.php?v=d&plugin=blea&modal=blea.divoomtimeboxmini.all').dialog('open');
								modifyWithoutSave=false;
							}
						});
					}
				},
			}
		});
	});

	$('.bt_renameImageMiniFile').on('click', function () {
		var oriname = $(this).closest('.miniImageName').attr('data-name');
		var newname = prompt("Quel nouveau nom voulez-vous donner à l'image? (sans extension)", "")
		if (newname == ''){
			$('.eventDisplayMini').showAlert({message:  'Vous devez spécifier un nom pour sauver une image',level: 'danger'});
			setTimeout(function() { deleteAlertMini()}, 2000);
			return;
		}
		bootbox.dialog({
			title: 'Etes-vous sur ?',
			message: 'Vous allez renommer l\'image : "' + oriname.charAt(0).toUpperCase() + oriname.slice(1) + '" en : "' + newname.charAt(0).toUpperCase() + newname.slice(1) + '" ! Voulez-vous continuer ?',
			buttons: {
				"{{Annuler}}": {
					className: "btn-danger",
					callback: function () {
					}
				},
				success: {
					label: "{{Continuer}}",
					className: "btn-success",
					callback: function () {
						$.ajax({
							type: "POST",
							url: "plugins/blea/core/config/devices/divoomtimeboxmini/ajax/divoomtimeboxmini.ajax.php",
							data: {
								action: "renameImageFile",
								oriname: oriname,
								newname: newname,

							},
							global : false,
							dataType: 'json',
							error: function(request, status, error) {
								handleAjaxError(request, status, error);
							},
							success: function(data) {
								if (data.state != 'ok') {
									$('.eventDisplayMini').showAlert({message:  data.result,level: 'danger'});
									setTimeout(function() { deleteAlertMini() }, 2000);
									return;
								}
								$('.eventDisplayMini').showAlert({message:  'Renommage effectué' ,level: 'success'});
								setTimeout(function() { deleteAlertMini() }, 2000);
								$('#md_modal2').dialog('close');
								$('#md_modal2').dialog({title: "{{Votre Collection}}"});
								$('#md_modal2').load('index.php?v=d&plugin=blea&modal=blea.divoomtimeboxmini.all').dialog('open');
								modifyWithoutSave=false;
							}
						});
					}
				},
			}
		});
	});

	function deleteAlertMini() {
		$('.eventDisplayMini').hideAlert();
	}

	$('#md_modal2').on('dialogclose', function () {
		loadMemoryList();
   });
</script>
