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
$eqLogics = array();
$antennas = array();
$remotes = blea_remote::all();
foreach ($remotes as $remote){
	$info = array();
	$name = $remote->getRemoteName();
	$info['x'] = $remote->getConfiguration('positionx',999);
	$info['y'] = $remote->getConfiguration('positiony',999);
	$antennas[$name]=$info;
}
$infolocal=array();
$infolocal['x'] = config::byKey('positionx', 'blea', 999);
$infolocal['y'] = config::byKey('positiony', 'blea', 999);
$antennas['local']=$infolocal;
foreach (eqLogic::byType('blea') as $eqLogic){
	$info =array();
	$info['name'] = $eqLogic->getName();
	$info['icon'] = $eqLogic->getConfiguration('iconModel');
	$info['rssi'] = array();
	foreach ($eqLogic->getCmd('info') as $cmd) {
		$logicalId = $cmd->getLogicalId();
		if (substr($logicalId,0,4) == 'rssi'){
			$remotename= substr($logicalId,4);
			$remoterssi = $cmd->execCmd();
			$info['rssi'][$remotename] = $remoterssi;
		}
	}
	$eqLogics[$eqLogic->getName()]=$info;
}
sendVarToJS('eqLogics', $eqLogics);
sendVarToJS('antennas', $antennas);
?>
<script type="text/javascript" src="plugins/blea/3rdparty/vivagraph/vivagraph.min.js"></script>
<style>
    #graph_network {
        height: 100%;
        width: 100%;
        position: absolute;
    }
    #graph_network > svg {
        height: 100%;
        width: 100%
    }
</style>
<div id="graph_network" class="tab-pane">
<a class="btn btn-success bleaRemoteAction" data-action="saveanttenna"><i class="fa fa-floppy-o"></i> {{Position Antennes}}</a>
<a class="btn btn-success bleaRemoteAction" data-action="refresh"><i class="fa fa-refresh"></i></a>
<i class="fa fa-question-circle" style="cursor:pointer;font-size:2em" title="{{Représentation relative de la puissance des liens sur les antennes. Vous pouvez déplacer les antennes et sauver leur position pour les retrouver à la même place. Concernant les équipements, ceux-ci prennent une position d'équilibre (vous pouvez aussi les déplacer mais ils s'équilibreront). Si les antennes sont toutes d'un coté de l'équipement, il peut y avoir plusieurs positions d'équilibres de part et d'autres. Cependant dans le cas d'un équipement avec des antennes autour de lui (le plus en triangle possible), il y aura une seule position d'équilibre qui sera proche de la réelle. Certains modules comme les NIU émettent que lors de l'appui, donc au bout d'un moment il n'y a plus de signal, à ce moment là les modules sont rattachés virtuellement à l'antenne local via des pointillés}}"></i>
</div>

<script>
load_graph();
function load_graph(){
    $('#graph_network svg').remove();
	var graph = Viva.Graph.graph();
	for (antenna in antennas) {
		if (antenna == 'local'){
			graph.addNode(antenna,{url : 'plugins/blea/3rdparty/jeeblue.png',antenna :1,x:antennas[antenna]['x'],y:antennas[antenna]['y']});
		} else {
			graph.addNode(antenna,{url : 'plugins/blea/3rdparty/antenna.png',antenna :1,x:antennas[antenna]['x'],y:antennas[antenna]['y']});
		}
		topin = graph.getNode(antenna);
		topin.isPinned = true;
	}
	for (eqlogic in eqLogics) {
		haslink = 0;
		graph.addNode(eqLogics[eqlogic]['name'],{url : 'plugins/blea/core/config/devices/'+eqLogics[eqlogic]['icon']+'.jpg',antenna :0});
		for (linkedantenna in eqLogics[eqlogic]['rssi']){
			signal = eqLogics[eqlogic]['rssi'][linkedantenna];
			orisignal = signal;
			if (signal == -200 || signal == ''){
				quality = 200;
			} else if(signal <= -100){
				quality = 0;
			} else if(signal >= -50){
				quality = 100;
			}else{
				quality = 2 * (signal + 100);
			}
			lenghtfactor = quality/100;
			if (lenghtfactor != 2){
				haslink=1;
				graph.addLink(linkedantenna,eqLogics[eqlogic]['name'],{isdash: 0,lengthfactor: lenghtfactor,signal : orisignal});
			}
		}
		if (haslink != 0){
			for (antenna in antennas){
				linked = 0;
				for (linkedantenna in eqLogics[eqlogic]['rssi']){
					if (antenna == linkedantenna && eqLogics[eqlogic]['rssi'][linkedantenna] != -200){
						linked = 1;
					}
				}
				if (linked == 0){
					graph.addLink(antenna,eqLogics[eqlogic]['name'],{isdash: 1,lengthfactor: -0.1,signal : -200});
				}
			}
		}
		if (haslink == 0){
			graph.addLink('local',eqLogics[eqlogic]['name'],{isdash: 1,lengthfactor: 0.5,signal : -200});
		}
	}
	var graphics = Viva.Graph.View.svgGraphics();
	highlightRelatedNodes = function (nodeId, isOn) {
                graph.forEachLinkedNode(nodeId, function (node, link) {
                    var linkUI = graphics.getLinkUI(link.id);
                    if (linkUI) {
                        linkUI.attr('stroke-width', isOn ? '2.2px' : '0.6px');
                    }
                });
            };
	graphics.node(function(node) {
		name = node.id;
		if (name == 'local'){
			name = 'Local';
		}
       var ui = Viva.Graph.svg('g'),
                  svgText = Viva.Graph.svg('text').attr('y', '-4px').text(name),
                  img = Viva.Graph.svg('image')
                     .attr('width', 48)
                     .attr('height', 48)
                     .link(node.data.url);
              ui.append(svgText);
              ui.append(img);
		$(ui).hover(function () {
                    highlightRelatedNodes(node.id, true);
                }, function () {
                    highlightRelatedNodes(node.id, false);
                });
                return ui;	
    })
    .placeNode(function(nodeUI, pos){
		nodeUI.attr('transform',
				'translate(' +
					(pos.x - 24) + ',' + (pos.y - 24) +
				')');
    });
	var idealLength =400;
	var layout = Viva.Graph.Layout.forceDirected(graph, {
                springLength: idealLength,
                stableThreshold: 0.1,
                dragCoeff: 0.02,
                springCoeff: 0.0005,
                gravity: -0.5,
                springTransform: function (link, spring) {
                    spring.length = idealLength * (1-link.data.lengthfactor);
                }
            });
	graphics.link(function (link) {
                dashvalue = '5, 0';
				color = 'green';
				if (link.data.signal <= -150) {
					color = 'grey';
				} else if (link.data.signal <= -92) {
					color = 'red';
				} else if (link.data.signal <= -86) {
					color = 'orange';
				} else if (link.data.signal <= -81) {
					color = 'yellow';
				}
                if (link.data.isdash == 1) {
                    dashvalue = '5, 2';
                }
                return Viva.Graph.svg('line').attr('stroke', color).attr('stroke-dasharray', dashvalue).attr('stroke-width', '0.6px');
            });
	for (antenna in antennas) {
		if (parseInt(antennas[antenna]['x']) != 999){
			layout.setNodePosition(antenna,parseInt(antennas[antenna]['x']),parseInt(antennas[antenna]['y']));
		}
}
	var renderer = Viva.Graph.View.renderer(graph,
    {
        graphics : graphics,
		layout : layout,
		prerender : 10000,
		container: document.getElementById('graph_network')
    });
renderer.run();
$('.bleaRemoteAction[data-action=refresh]').on('click',function(){
	$('#md_modal').dialog('close');
	$('#md_modal').dialog({title: "{{Réseau BLEA}}"});
	$('#md_modal').load('index.php?v=d&plugin=blea&modal=blea.graph&id=blea').dialog('open');
});
$('.bleaRemoteAction[data-action=saveanttenna]').on('click',function(){
	var antenna= {}
	graph.forEachNode(function (node) {
	if (node.data.antenna == 1){
  var position = layout.getNodePosition(node.id);
  antenna[node.id] = position.x +'|'+position.y;
	}
});

$.ajax({// fonction permettant de faire de l'ajax
            type: "POST", // méthode de transmission des données au fichier php
            url: "plugins/blea/core/ajax/blea.ajax.php", // url du fichier php
            data: {
                action: "saveAntennaPosition",
				antennas: json_encode(antenna)
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
		$('#div_alert').showAlert({message: 'Positions des antennes sauvées avec succès', level: 'success'});
		$('#md_modal').dialog('close');
		$('#md_modal').dialog({title: "{{Réseau BLEA}}"});
		$('#md_modal').load('index.php?v=d&plugin=blea&modal=blea.graph&id=blea').dialog('open');
        }
    });
});

}
</script>