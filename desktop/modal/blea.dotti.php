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
if (init('id') == '') {
	throw new Exception('{{L\'id de l\'équipement ne peut etre vide : }}' . init('op_id'));
}
sendVarToJS('id', init('id'));
?>

<div class="row" style="height:100%; width: 100%">
	<div class="col-lg-2">
		<div class="form-group">
			<span style="margin-right:15px;"><label class="fa fa-circle pixelCircle" style="color : #000000;font-size:2em; margin-top:10px;margin-left:15px; cursor: pointer;"><input class="pixelcolor" type="color" value="#000000" style="width:0;height:0;visibility:hidden"></label>{{Couleur}}</span>
		</div>
		<div class="form-group">
			<a class="btn btn-xs btn-success" id="bt_fill" style="margin-left:20px"><i class="fa fa-tint"></i> {{Remplir}}</a>
		</div>
		<div class="form-group">
			<a class="btn btn-xs btn-danger" id="bt_fillblack" style="margin-left:20px"><i class="fa fa-times"></i> {{Vider}}</a>
		</div>
		<div class="form-group">
			<a class="btn btn-xs btn-warning replacecolor" id="bt_replace" style="margin-left:20px;"><i class="fa fa-flask"></i> {{Pot de peinture}}</a>
		</div>
		<div class="form-group">
			<a class="btn btn-xs btn-success copycolor" id="bt_copyColor" style="margin-left:20px"><i class="fa fa-pencil"></i> {{Pipette}}</a>
		</div>
		<div class="form-group">
			<a class="btn btn-xs btn-danger erasecolor" id="bt_erase" style="margin-left:20px"><i class="fa fa-eraser"></i> {{Gommer}}</a>
		</div>
		<div class="form-group">
			<label class="checkbox-inline"><input class="realtime" type="checkbox" unchecked />{{Temps réel}}</label>
		</div>
		<div class="form-group">
			<label class="checkbox-inline"><input class="realimage" type="checkbox" unchecked />{{Regrouper pixel}}</label>
		</div>
		<div class="form-group">
			<div class="eventDisplay"></div>
		</div>
	</div>
	<div class="col-lg-6">
		<center>
			<?php
$i = 1;
while ($i < 65) {
	$j = 1;
	while ($j < 9) {
		$notfirstline = ' pixelFirstLine';
		if ($i >= 9){
			$notfirstline = ' pixelNotFirstLine';
		}
		echo '<label class="fa fa-square pixel' . $notfirstline .'" data-pixel="' . $i . '" style="color : #000000;font-size:4.6em; margin-top:10px;margin-left:15px; cursor: pointer;border-radius:0"></label>  ';
		$j++;
		$i++;
		
	}
	echo '<br/>';
}
?>
		</center>
	</div>
	<div class="col-lg-4">
		<div class="form-group">
			<a class="btn btn-warning" id="bt_sendAll"><i class="fa fa-paint-brush"></i> {{Afficher sur le Dotti}}</a>
			<a class="btn btn-success" id="bt_displayExport"><i class="fa fa-download"></i></a>
			<a class="btn btn-danger" id="bt_Import"><i class="fa fa-upload"></i></a>
			<span class="biblioNumber pull-right label label-info" style="font-size:1em;cursor:pointer">
			</span>
		</div>
		<div class="form-group">
			<div class="input-group">
				<input class="nameDottiScreen form-control" id="texte" type='text'/>
				<span class="input-group-btn">
					<a class="btn btn-success" id="bt_saveImage"><i class="fa fa-floppy-o"></i></a>
				</span>
			</div>
		</div>
		<div class="form-group">
			<div class="input-group">
				<select class="memoryload form-control"></select>
				<span class="input-group-btn">
					<a class="btn btn-danger" id="bt_delImage"><i class="fa fa-trash-o"></i></a>
				</span>
			</div>
		</div>
		<div class="form-group">
			<textarea class="imageDotti form-control" style="display:none" rows="20"></textarea></br>
			<a class="btn btn-success uploadimageDotti" id="bt_upload" style="display:none"><i class="fa fa-check"></i></a>
			<a class="btn btn-danger closeimageDotti" id="bt_close" style="display:none"><i class="fa fa-times"></i></a>
		</div>
	</div>
</div>
<script>
	loadMemoryList();
	setTimeout(function() { loadImage()}, 200);
	var pencil = 0;
	var erase = 0;
	var replace = 0;
	$('.realimage').on('change', function () {
		if ($(this).is(':checked')){
			$('.pixelNotFirstLine').css('margin-top' , '-17px');
			$('.pixel').css('margin-left' , '-6px');
			$('.pixelFirstLine').attr('class', 'fa fa-stop pixel pixelFirstLine');
			$('.pixelNotFirstLine').attr('class', 'fa fa-stop pixel pixelNotFirstLine');
		} else {
			$('.pixel').css('margin-top' , '10px');
			$('.pixel').css('margin-left' , '15px');
			$('.pixelFirstLine').attr('class', 'fa fa-square pixel pixelFirstLine');
			$('.pixelNotFirstLine').attr('class', 'fa fa-square pixel pixelNotFirstLine');
		}
	});
	$('#bt_erase').on('click', function () {
		if (erase == 0){
			erase = 1;
			pencil = 0;
			replace = 0;
			$('.erasecolor').css('color' , '#000080');
			$('.replacecolor').css('color' , '');
			$('.copycolor').css('color' , '');
			$('.eventDisplay').hideAlert();
			$('.eventDisplay').showAlert({message:  'Vous êtes en mode gomme. Effacer les pixels que vous voulez puis recliquez sur Gommer pour sortir du mode',level: 'danger'});
		} else {
			erase = 0;
			$('.erasecolor').css('color' , '');
			$('.eventDisplay').hideAlert();
		}
	});
	$('#bt_replace').on('click', function () {
		if (replace == 0){
			replace = 1;
			pencil = 0;
			erase = 0;
			$('.replacecolor').css('color' , '#000080');
			$('.erasecolor').css('color' , '');
			$('.copycolor').css('color' , '');
			$('.eventDisplay').hideAlert();
			$('.eventDisplay').showAlert({message:  'Vous êtes en mode pot de peinture. Cliquez sur une couleur à remplacer',level: 'warning'});
		} else {
			replace = 0;
			$('.replacecolor').css('color' , '');
			$('.eventDisplay').hideAlert();
		}
	});
	$('#bt_copyColor').on('click', function () {
		if (pencil == 0){
			pencil = 1;
			erase =0;
			replace = 0;
			$('.copycolor').css('color' , '#000080');
			$('.replacecolor').css('color' , '');
			$('.erasecolor').css('color' , '');
			$('.eventDisplay').hideAlert();
			$('.eventDisplay').showAlert({message:  'Vous êtes en mode pipette. Choisissez la couleur ou sortez du mode en recliquant sur Pipette',level: 'warning'});
		} else {
			pencil = 0;
			$('.eventDisplay').hideAlert();
			$('.copycolor').css('color' , '');
		}
	});
	$('#bt_displayExport').on('click', function () {
		$('.imageDotti').show();
		$('.closeimageDotti').show();
		$('.uploadimageDotti').hide();
		getImageCode();
	});
	
	$('.biblioNumber').on('click', function () {
    $('#md_modal2').dialog({title: "{{Votre Collection}}"});
    $('#md_modal2').load('index.php?v=d&plugin=blea&modal=blea.dotti.all').dialog('open');
});

	function autoLoadJson(){
		try {
			data = json_decode($('.imageDotti').val());
			for(var pixelId in data){
				$('[data-pixel="'+ pixelId +'"]').css('color', data[pixelId]);
			}
		}catch (e) {
		}
	}
	
	$('.imageDotti').on('change',function(){
		autoLoadJson();
	});

	$('#bt_Import').on('click', function () {
		$('.imageDotti').show();
		$('.closeimageDotti').show();
		$('.uploadimageDotti').show();
		$('.imageDotti').val('');
	});
	$('#bt_close').on('click', function () {
		$('.imageDotti').hide();
		$('.closeimageDotti').hide();
		$('.uploadimageDotti').hide();
	});
	
	$('#bt_saveImage').on('click', function () {
		var array = {};
		$('.pixel').each(function( index ) {
			array[$(this).attr('data-pixel')] = hexc($(this).css('color'));
		});
		if ($('.nameDottiScreen').val() == ''){
			$('.eventDisplay').showAlert({message:  'Vous devez spécifier un nom pour sauver une image',level: 'danger'});
			setTimeout(function() { deleteAlert()}, 2000);
			return;
		}
		bootbox.dialog({
			title: 'Etes-vous sur ?',
			message: 'Vous allez sauver l\'image avec le nom "' +$('.nameDottiScreen').val() +'" ! Voulez-vous continuer ?',
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
						$('.eventDisplay').showAlert({message:  'Affichage sur le Dotti en cours ...',level: 'warning'});
						$.ajax({
							type: "POST",
							url: "plugins/blea/core/config/devices/dotti/ajax/dotti.ajax.php",
							data: {
								action: "saveImage",
								id: id,
								name: $('.nameDottiScreen').val(),
								data : array
							},
							global : false,
							dataType: 'json',
							error: function(request, status, error) {
								handleAjaxError(request, status, error);
							},
							success: function(data) {
								if (data.state != 'ok') {
									$('.eventDisplay').showAlert({message:  data.result,level: 'danger'});
									setTimeout(function() { deleteAlert()}, 2000);
									return;
								}
								$('.eventDisplay').showAlert({message:  'Sauvegarde effectuée' ,level: 'success'});
								setTimeout(function() { deleteAlert() }, 2000);
								modifyWithoutSave=false;
								loadMemoryList();
							}
						});
					}
				},
			}
		});
	});

	$('.memoryload').on('change', function () {
		getImageCode();
		loadImage();
		if ($('.realtime').is(':checked')){
			setTimeout(function() { sendAll() }, 500);
		}
	});

	$('#bt_delImage').on('click', function () {
		bootbox.dialog({
			title: 'Etes-vous sur ?',
			message: 'Vous allez supprimer l\'image avec le nom "' +$('.memoryload').find('option:selected').text() +'" ! Voulez-vous continuer ?',
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
							url: "plugins/blea/core/config/devices/dotti/ajax/dotti.ajax.php",
							data: {
								action: "delImage",
								name: $('.memoryload').val()
							},
							global : false,
							dataType: 'json',
							error: function(request, status, error) {
								handleAjaxError(request, status, error);
							},
							success: function(data) {
								if (data.state != 'ok') {
									$('.eventDisplay').showAlert({message:  data.result,level: 'danger'});
									setTimeout(function() { deleteAlert() }, 2000);
									return;
								}
								$('.eventDisplay').showAlert({message:  'Suppression effectuée' ,level: 'success'});
								setTimeout(function() { deleteAlert() }, 2000);
								loadMemoryList();
								modifyWithoutSave=false;
							}
						});
					}
				},
			}
		});
	});

	$('.pixel').on('click', function() {
		var pixelId = $(this).attr('data-pixel');
		var color = $('.pixelCircle').css('color');
		if (erase == 1){
			color ='rgb(0, 0, 0)';
		}
		if (pencil == 1){
			$('.pixelCircle').css('color', $(this).css('color'));
			$('.pixelcolor').val(hexc($(this).css('color')));
			pencil = 0;
			$('.eventDisplay').hideAlert();
			$('.copycolor').css('color' , '');
			return;
		}
		if (replace ==1){
			var array ={};
			var colortoreplace = $(this).css('color');
			$('.pixel').each(function( index ) {
				if ($(this).css('color') == colortoreplace ){
					array[$(this).attr('data-pixel')] = hexc(color);
					$(this).css('color', color);
				}
			});
			replace = 0;
			$('.eventDisplay').hideAlert();
			$('.replacecolor').css('color' , '');
			if ($('.realtime').is(':checked')){
				sendPixelArray(array,id);
			}
			return;
		}
		$(this).css('color', color);
		if ($('.realtime').is(':checked')){
			var array = {};
			array[pixelId.toString()] = hexc(color);
			sendPixelArray(array,id,false);
		}
	})

	$('.pixelcolor').on('change', function() {
		$(this).closest('.pixelCircle').css('color', $(this).val())
	})

	$('#bt_fill').on('click', function() {
		$('.pixel').each(function( index ) {
			$(this).css('color', $('.pixelCircle').css('color'));
		});
		if ($('.realtime').is(':checked')){
			var array = {};
			$('.pixel').each(function( index ) {
				array[$(this).attr('data-pixel')] = hexc($(this).css('color'));
			});
			sendPixelArray(array,id);
		}
	})
	
	$('#bt_fillblack').on('click', function() {
		$('.pixel').each(function( index ) {
			$(this).css('color', '#000000');
		});
		if ($('.realtime').is(':checked')){
			var array = {};
			$('.pixel').each(function( index ) {
				array[$(this).attr('data-pixel')] = '#000000';
			});
			sendPixelArray(array,id);
		}
	})

	$('#bt_sendAll').on('click', function() {
		sendAll();
	});
	
	function sendAll() {
		var array = {};
		$('.pixel').each(function( index ) {
			array[$(this).attr('data-pixel')] = hexc($(this).css('color'));
		});
		sendPixelArray(array,id);
	}
	
	function hexc(colorval) {
		var parts = colorval.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
		delete(parts[0]);
		for (var i = 1; i <= 3; ++i) {
			parts[i] = parseInt(parts[i]).toString(16);
			if (parts[i].length == 1) parts[i] = '0' + parts[i];
		}
		color = '#' + parts.join('');
		return color;
	}

	function sendPixelArray(_array,_id,_displaymess = true) {
		if (_displaymess){
			$('.eventDisplay').showAlert({message:  'Affichage sur le Dotti en cours ...' ,level: 'warning'});
		}
		$.ajax({
			type: "POST",
			url: "plugins/blea/core/config/devices/dotti/ajax/dotti.ajax.php",
			data: {
				action: "sendPixelArray",
				array: _array,
				id: _id
			},
			global: false,
			dataType: 'json',
			error: function(request, status, error) {
				handleAjaxError(request, status, error);
			},
			success: function(data) {
				if (data.state != 'ok') {
					$('.eventDisplay').showAlert({message:  data.result,level: 'danger'});
					setTimeout(function() { deleteAlert() }, 2000);
					return;
				}
				if (_displaymess){
					setTimeout(function() { $('.eventDisplay').showAlert({message:  'Affichage effectué' ,level: 'success'}); }, 2000);
					setTimeout(function() { deleteAlert() }, 4000);
				}
				modifyWithoutSave=false;
			}
		});
	}
	
	function deleteAlert() {
		$('.eventDisplay').hideAlert();
	}

	function loadMemoryList() {
		$.ajax({
			type: "POST",
			url: "plugins/blea/core/config/devices/dotti/ajax/dotti.ajax.php",
			data: {
				action: "loadMemoryList"
			},
			global:false,
			dataType: 'json',
			error: function(request, status, error) {
				handleAjaxError(request, status, error);
			},
			success: function(data) {
				if (data.state != 'ok') {
					$('.eventDisplay').showAlert({message:  data.result,level: 'danger'});
					setTimeout(function() { deleteAlert() }, 2000);
					return;
				}
				modifyWithoutSave=false;
				if (data.result){
					$('.memoryload').empty().append(data.result);
					$('.biblioNumber').empty().append(data.result.split('<option').length-1 + ' icônes');
				} else {
					$('.memoryload').empty();
				}
			}
		});
	}
	function loadImage(){
		$.ajax({
			type: "POST",
			url: "plugins/blea/core/config/devices/dotti/ajax/dotti.ajax.php",
			data: {
				action: "loadImage",
				name: $('.memoryload').val()
			},
			dataType: 'json',
			global: false,
			error: function(request, status, error) {
				handleAjaxError(request, status, error);
			},
			success: function(data) {
				if (data.state != 'ok') {
					$('.eventDisplay').showAlert({message:  data.result,level: 'danger'});
					setTimeout(function() { deleteAlert() }, 2000);
					return;
				}
				if (!$.isEmptyObject(data.result)){
					for(var pixelId in data.result){
						$('[data-pixel="'+ pixelId.toString() +'"]').css('color', data.result[pixelId]);
					}
				}
				$('.nameDottiScreen').val($('.memoryload').find('option:selected').text());
				modifyWithoutSave=false;
			}
		});
	}
	
	function getImageCode(){
		$('.imageDotti').val('');
		$.ajax({
			type: "POST",
			url: "plugins/blea/core/config/devices/dotti/ajax/dotti.ajax.php",
			data: {
				action: "getImageCode",
				name: $('.memoryload').val()
			},
			dataType: 'json',
			global: false,
			error: function(request, status, error) {
				handleAjaxError(request, status, error);
			},
			success: function(data) {
				if (data.state != 'ok') {
					$('.eventDisplay').showAlert({message:  data.result,level: 'danger'});
					setTimeout(function() { deleteAlert()}, 2000);
					return;
				}
				$('.imageDotti').off('change');
				$('.imageDotti').val(data.result);
				autoLoadJson();
				modifyWithoutSave=false;
			}
		});
	}
</script>
