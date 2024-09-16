
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
 
  $('#bt_resetSearch').off('click').on('click', function () {
     $('#in_searchEqlogic').val('')
     $('#in_searchEqlogic').keyup();
 })
 
 $('.changeIncludeState').on('click', function () {
	var mode = $(this).attr('data-mode');
	var state = $(this).attr('data-state');
	var list = '';
	if (state == 1){
		$.ajax({// fonction permettant de faire de l'ajax
			type: "POST", // methode de transmission des données au fichier php
			url: "plugins/blea/core/ajax/blea.ajax.php", // url du fichier php
			data: {
				action: "getAllTypes",
			},
			dataType: 'json',
			global: true,
			async: false,
			error: function (request, status, error) {
				handleAjaxError(request, status, error);
			},
			success: function (data) { // si l'appel a bien fonctionné
			if (data.state != 'ok') {
				$('#div_alert').showAlert({message: data.result, level: 'danger'});
				return;
			}
			list = data['result'];
			}
		});
		var dialog_title = '';
		var dialog_message = '<form class="form-horizontal onsubmit="return false;"> ';
		dialog_title = '{{Inclusion BLEA}}';
		dialog_message += '<label class="control-label" > {{Quel type de produit voulez-vous inclure : }} </label> ' +
		'<div>' +
		' <select id="type">' +
		'<option value="all">{{Tous}}</option>';
		for (device in list) {
			dialog_message += '<option value="'+list[device]+'"> '+device+'</option>';
		}
		dialog_message += '</select></div><br>'+
		'<label class="lbl lbl-warning" for="type">{{Choisissez le type de produit que vous souhaitez ajouter}}</label> ';
		dialog_message += '</form>';
		bootbox.dialog({
			title: dialog_title,
			message: dialog_message,
			buttons: {
				"{{Annuler}}": {
					className: "btn-danger",
					callback: function () {
					}
				},
				success: {
					label: "{{Démarrer}}",
					className: "btn-success",
					callback: function () {
						var proto = $("#type option:selected").val();
						changeIncludeState(state, mode ,proto);
					}
				},
			}
		})
	} else {
		changeIncludeState(state, mode);
	}
});

$("#bt_addVirtualInfo").on('click', function (event) {
  addCmdToTable({type: 'info'});
  modifyWithoutSave = true;
});

 $('#bt_healthblea').on('click', function () {
    $('#md_modal').dialog({title: "{{Santé BLEA}}"});
    $('#md_modal').load('index.php?v=d&plugin=blea&modal=health').dialog('open');
});

$('#bt_graphblea').on('click', function () {
    $('#md_modal').dialog({title: "{{Réseau BLEA}}"});
    $('#md_modal').load('index.php?v=d&plugin=blea&modal=blea.graph').dialog('open');
});

$('#bt_specificmodal').on('click', function () {
    $('#md_modal').dialog({title: "{{Configuration spécifique}}"});
    $('#md_modal').load('index.php?v=d&plugin=blea&modal=' +$(this).attr("data-modal") +'&id='+$('.eqLogicAttr[data-l1key=id]').val()).dialog('open');
});

$('#bt_remoteblea').on('click', function () {
    $('#md_modal').dialog({title: "{{Gestion des antennes bluetooth}}"});
    $('#md_modal').load('index.php?v=d&plugin=blea&modal=blea.remote&id=blea').dialog('open');
});

$('#bt_advancedblea').on('click', function () {
    $('#md_modal').dialog({title: "{{Réglages avancées}}"});
    $('#md_modal').load('index.php?v=d&plugin=blea&modal=blea.advanced').dialog('open');
});

 $('.eqLogicAttr[data-l1key=configuration][data-l2key=device]').on('change', function () {
  if($('.li_eqLogic.active').attr('data-eqlogic_id') != ''){
   getModelListParam($(this).value(),$('.eqLogicAttr[data-l1key=id]').value());
}else{
    $('#img_device').attr("src",'plugins/blea/doc/images/blea_icon.png');
}
});

function getModelListParam(_conf,_id) {
    $.ajax({// fonction permettant de faire de l'ajax
        type: "POST", // methode de transmission des données au fichier php
        url: "plugins/blea/core/ajax/blea.ajax.php", // url du fichier php
        data: {
            action: "getModelListParam",
            conf: _conf,
            id: _id,
        },
        dataType: 'json',
        global: false,
        error: function (request, status, error) {
            handleAjaxError(request, status, error);
        },
        success: function (data) { // si l'appel a bien fonctionné
        if (data.state != 'ok') {
            $('#div_alert').showAlert({message: data.result, level: 'danger'});
            return;
        }
        var options = '';
        for (var i in data.result[0]) {
            if (data.result[0][i]['selected'] == 1){
                options += '<option value="'+i+'" selected>'+data.result[0][i]['value']+'</option>';
            } else {
                options += '<option value="'+i+'">'+data.result[0][i]['value']+'</option>';
            }
        }
		if (data.result[2] != false){
             $(".globalRemark").show();
             $(".globalRemark").empty().append(data.result[2]);
         } else {
			 $(".globalRemark").empty()
             $(".globalRemark").hide();
         }
		 if (data.result[3] != false){
             $(".specificmodal").show();
			 $(".specificmodal").attr('data-modal', data.result[3]);
         } else {
             $(".specificmodal").hide();
         }
        $(".modelList").show();
        $(".listModel").html(options);
		$icon = $('.eqLogicAttr[data-l1key=configuration][data-l2key=iconModel]').value();
		if($icon != '' && $icon != null){
			$('#img_device').attr("src", 'plugins/blea/core/config/devices/'+$icon+'.jpg');
		}
    }
});
}

$('#bt_autoDetectModule').on('click', function () {
    var dialog_title = '{{Recharge configuration}}';
    var dialog_message = '<form class="form-horizontal onsubmit="return false;"> ';
    dialog_title = '{{Recharger la configuration}}';
    dialog_message += '<label class="control-label" > {{Sélectionner le mode de rechargement de la configuration ?}} </label> ' +
    '<div> <div class="radio"> <label > ' +
    '<input type="radio" name="command" id="command-0" value="0" checked="checked"> {{Sans supprimer les commandes}} </label> ' +
    '</div><div class="radio"> <label > ' +
    '<input type="radio" name="command" id="command-1" value="1"> {{En supprimant et recréant les commandes}}</label> ' +
    '</div> ' +
    '</div><br>' +
    '<label class="lbl lbl-warning" for="name">{{Attention, "En supprimant et recréant" va supprimer les commandes existantes.}}</label> ';
    dialog_message += '</form>';
    bootbox.dialog({
       title: dialog_title,
       message: dialog_message,
       buttons: {
           "{{Annuler}}": {
               className: "btn-danger",
               callback: function () {
               }
           },
           success: {
               label: "{{Démarrer}}",
               className: "btn-success",
               callback: function () {
                    if ($("input[name='command']:checked").val() == "1"){
						bootbox.confirm('{{Etes-vous sûr de vouloir récréer toutes les commandes ? Cela va supprimer les commandes existantes}}', function (result) {
                            if (result) {
                                $.ajax({
                                    type: "POST",
                                    url: "plugins/blea/core/ajax/blea.ajax.php",
                                    data: {
                                        action: "autoDetectModule",
                                        id: $('.eqLogicAttr[data-l1key=id]').value(),
                                        createcommand: 1,
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
                                        $('#div_alert').showAlert({message: '{{Opération réalisée avec succès}}', level: 'success'});
                                    }
                                });
                            }
                        });
					} else {
						$.ajax({
                                    type: "POST",
                                    url: "plugins/blea/core/ajax/blea.ajax.php",
                                    data: {
                                        action: "autoDetectModule",
                                        id: $('.eqLogicAttr[data-l1key=id]').value(),
                                        createcommand: 0,
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
                                        $('#div_alert').showAlert({message: '{{Opération réalisée avec succès}}', level: 'success'});
                                    }
                                });
					}
            }
        },
    }
});
});

$('.deleteUnknown').on('click', function () {
    bootbox.confirm('{{Etes-vous sûr de vouloir supprimer tous les devices inconnus ? Cela supprimera que les devices Inconnus qui ne sont pas attribués à un objet. }}', function (result) {
        if (result) {
            $.ajax({
                type: "POST",
                url: "plugins/blea/core/ajax/blea.ajax.php",
                data: {
                    action: "deleteUnknown",
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
                    $('#div_alert').showAlert({message: '{{Opération réalisée avec succès}}', level: 'success'});
					window.location.reload();
                }
            });
        }
    });
});

 $('.eqLogicAttr[data-l1key=configuration][data-l2key=iconModel]').on('change', function () {
  if($(this).value() != '' && $(this).value() != null){
    $('#img_device').attr("src", 'plugins/blea/core/config/devices/'+$(this).value()+'.jpg');
}
});

$("#table_cmd").sortable({axis: "y", cursor: "move", items: ".cmd", placeholder: "ui-state-highlight", tolerance: "intersect", forcePlaceholderSize: true});


function addCmdToTable(_cmd) {
    if (!isset(_cmd)) {
        var _cmd = {configuration: {}};
    }
    var tr = '<tr class="cmd" data-cmd_id="' + init(_cmd.id) + '">';
    tr += '<td>';
    tr += '<div class="row">';
    tr += '<div class="col-sm-6">';
    tr += '<a class="cmdAction btn btn-default btn-sm" data-l1key="chooseIcon"><i class="fas fa-flag"></i> Icône</a>';
    tr += '<span class="cmdAttr" data-l1key="display" data-l2key="icon" style="margin-left : 10px;"></span>';
    tr += '</div>';
    tr += '<div class="col-sm-6">';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="name">';
    tr += '</div>';
    tr += '</div>';
    tr += '<select class="cmdAttr form-control input-sm" data-l1key="value" style="display : none;margin-top : 5px;" title="La valeur de la commande vaut par défaut la commande">';
    tr += '<option value="">Aucune</option>';
    tr += '</select>';
    tr += '</td>';
    tr += '<td>';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="id" style="display : none;">';
    tr += '<span class="type" type="' + init(_cmd.type) + '">' + jeedom.cmd.availableType() + '</span>';
    tr += '<span class="subType" subType="' + init(_cmd.subType) + '"></span>';
    tr += '</td>';
    tr += '<td><input class="cmdAttr form-control input-sm" data-l1key="logicalId" value="0" style="width : 70%; display : inline-block;" placeholder="{{Commande}}"><br/>';
    tr += '</td>';
    tr += '<td>';
    tr += '<span><label class="checkbox-inline"><input type="checkbox" class="cmdAttr checkbox-inline" data-l1key="isVisible" checked/>{{Afficher}}</label></span> ';
    tr += '<span><label class="checkbox-inline"><input type="checkbox" class="cmdAttr checkbox-inline" data-l1key="isHistorized" checked/>{{Historiser}}</label></span> ';
    tr += '<span><label class="checkbox-inline"><input type="checkbox" class="cmdAttr" data-l1key="display" data-l2key="invertBinary"/>{{Inverser}}</label></span> ';
    tr += '<br/><input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="returnStateValue" placeholder="{{Valeur retour d\'état}}" style="width : 20%; display : inline-block;margin-top : 5px;margin-right : 5px;">';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="returnStateTime" placeholder="{{Durée avant retour d\'état (min)}}" style="width : 20%; display : inline-block;margin-top : 5px;margin-right : 5px;">';
    tr += '</td>';
    tr += '<td>';
    tr += '<select class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="updateCmdId" style="display : none;margin-top : 5px;" title="Commande d\'information à mettre à jour">';
    tr += '<option value="">Aucune</option>';
    tr += '</select>';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="updateCmdToValue" placeholder="Valeur de l\'information" style="display : none;margin-top : 5px;">';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="unite"  style="width : 100px;" placeholder="Unité" title="Unité">';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="minValue" placeholder="Min" title="Min"> ';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="maxValue" placeholder="Max" title="Max" style="margin-top : 5px;">';
    tr += '</td>';
    tr += '<td>';
    if (is_numeric(_cmd.id)) {
        tr += '<a class="btn btn-default btn-xs cmdAction" data-action="configure"><i class="fas fa-cogs"></i></a> ';
        tr += '<a class="btn btn-default btn-xs cmdAction" data-action="test"><i class="fas fa-rss"></i> {{Tester}}</a>';
    }
    tr += '<i class="fas fa-minus-circle pull-right cmdAction cursor" data-action="remove"></i></td>';
    tr += '</tr>';
    $('#table_cmd tbody').append(tr);
    var tr = $('#table_cmd tbody tr:last');
    jeedom.eqLogic.builSelectCmd({
        id: $('.eqLogicAttr[data-l1key=id]').value(),
        filter: {type: 'info'},
        error: function (error) {
            $('#div_alert').showAlert({message: error.message, level: 'danger'});
        },
        success: function (result) {
            tr.find('.cmdAttr[data-l1key=value]').append(result);
            tr.find('.cmdAttr[data-l1key=configuration][data-l2key=updateCmdId]').append(result);
            tr.setValues(_cmd, '.cmdAttr');
            jeedom.cmd.changeType(tr, init(_cmd.subType));
        }
    });
}

$('body').on('blea::includeState', function (_event,_options) {
	if (_options['mode'] == 'learn') {
		if (_options['state'] == 1) {
			if($('.include').attr('data-state') != 0){
				$.hideAlert();
				$('.include:not(.card)').removeClass('btn-default').addClass('btn-success');
				$('.include').attr('data-state', 0);
				$('.include').empty().append('<i class="fas fa-spinner fa-pulse"></i><br/><span>{{Arrêter Scan}}</span>');
				$('#div_inclusionAlert').showAlert({message: '{{Vous êtes en mode scan. Recliquez sur le bouton scan pour sortir de ce mode (sinon le mode restera actif une minute)}}', level: 'warning'});
			}
		} else {
			if($('.include').attr('data-state') != 1){
				$.hideAlert();
				$('.include:not(.card)').addClass('btn-default').removeClass('btn-success btn-danger');
				$('.include').attr('data-state', 1);
				$('.include').empty().append('<i class="fas fa-bullseye"></i><br/><span>{{Lancer Scan}}</span>');
			}
		}
	}
});

$('body').on('blea::includeDevice', function (_event,_options) {
    if (modifyWithoutSave) {
        $('#div_inclusionAlert').showAlert({message: '{{Un périphérique vient d\'être inclu/exclu. Veuillez réactualiser la page}}', level: 'warning'});
    } else {
        if (_options == '') {
            window.location.reload();
        } else {
            window.location.href = 'index.php?v=d&p=blea&m=blea&id=' + _options;
        }
    }
});


function changeIncludeState(_state,_mode,_type='') {
    $.ajax({// fonction permettant de faire de l'ajax
        type: "POST", // methode de transmission des données au fichier php
        url: "plugins/blea/core/ajax/blea.ajax.php", // url du fichier php
        data: {
            action: "changeIncludeState",
            state: _state,
            mode: _mode,
            type: _type,
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
    }
});
}
