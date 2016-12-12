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
$antennas = array('local');
$remotes = blea_remote::all();
foreach ($remotes as $remote){
	$name = $remote->getRemoteName();
	$antennas[]=$name;
}
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
	<div id="graph-node-name"></div>
</div>

<script>
load_graph();
function load_graph(){
    $('#graph_network svg').remove();
	var graph = Viva.Graph.graph();
	
	for (antenna in antennas) {
		if (antennas[antenna] == 'local'){
			graph.addNode(antennas[antenna],{url : 'plugins/blea/3rdparty/jeedom.png'});
		} else {
			graph.addNode(antennas[antenna],{url : 'plugins/blea/3rdparty/antenna.png'});
		}
		topin = graph.getNode(antennas[antenna]);
		topin.isPinned = true;
	}
	for (eqlogic in eqLogics) {
		haslink = 0;
		graph.addNode(eqLogics[eqlogic]['name'],{url : 'plugins/blea/core/config/devices/'+eqLogics[eqlogic]['icon']+'.jpg'});
		for (linkedantenna in eqLogics[eqlogic]['rssi']){
			signal = eqLogics[eqlogic]['rssi'][linkedantenna];
			orisignal = signal;
			if(signal <= -100){
				quality = 0;
			} else if(signal >= -50){
				quality = 100;
			}else{
				quality = 2 * (signal + 100);
			}
			lenghtfactor = quality/100;
			if (lenghtfactor != 999){
				haslink=1;
				graph.addLink(linkedantenna,eqLogics[eqlogic]['name'],{isdash: 0,lengthfactor: lenghtfactor,signal : orisignal});
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
				if (link.data.signal <= -100) {
					color = 'grey';
				} else if (link.data.signal <= -91) {
					color = 'red';
				} else if (link.data.signal <= -81) {
					color = 'orange';
				}
                if (link.data.isdash == 1) {
                    dashvalue = '5, 2';
                }
                return Viva.Graph.svg('line').attr('stroke', color).attr('stroke-dasharray', dashvalue).attr('stroke-width', '0.6px');
            });
	var renderer = Viva.Graph.View.renderer(graph,
    {
        graphics : graphics,
		layout : layout,
		prerender: 1200,
		container: document.getElementById('graph_network')
    });
renderer.run();
}
</script>