/* This file is part of Plugin openzwave for jeedom.
 *
 * Plugin openzwave for jeedom is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Plugin openzwave for jeedom is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Plugin openzwave for jeedom. If not, see <http://www.gnu.org/licenses/>.
 */

 function initBleaBlea() {
	$.ajax({
        type: "POST",
        url: "plugins/blea/core/ajax/blea.ajax.php",
        data: {
            action: "getMobileHealth",
        },
        dataType: 'json',
        error: function (request, status, error) {
            handleAjaxError(request, status, error);
		},
        success: function (data) { // si l'appel a bien fonctionné
        if (data.state != 'ok') {
            $('#div_inclusionAlert').showAlert({message: data.result, level: 'danger'});
            return;
		}
		$("#table_healthblea tbody").append(data.result)
        }
});

	$.ajax({
        type: "POST",
        url: "plugins/blea/core/ajax/blea.ajax.php",
        data: {
            action: "getMobileGraph",
        },
        dataType: 'json',
        error: function (request, status, error) {
            handleAjaxError(request, status, error);
		},
        success: function (data) { // si l'appel a bien fonctionné
        if (data.state != 'ok') {
            $('#div_inclusionAlert').showAlert({message: data.result, level: 'danger'});
            return;
		}
		eqLogics = data.result[0];
		antennas = data.result[1];
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
					graph.addLink(antenna,eqLogics[eqlogic]['name'],{isdash: 1,lengthfactor: -0.2,signal : -200});
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
}
});
 }

 
	$('.changeIncludeState').on('click', function () {
	var mode = $(this).attr('data-mode');
	var state = $(this).attr('data-state');
	changeIncludeState(state, mode);
});
$('.health').on('click', function () {
	$('.healthtable').show();
	$('.graph_network').hide();
});
$('.reseau').on('click', function () {
	$('.healthtable').hide();
	$('.graph_network').show();
});
	
    $('body').on('blea::includeState', function (_event,_options) {
	if (_options['mode'] == 'learn') {
		if (_options['state'] == 1) {
			$('.includestop').show();
			$('.include').hide();
		} else {
			$('.includestop').hide();
			$('.include').show();
		}
	}
});

    $('body').on('blea::includeDevice', function (_event,_options) {
      $('.eqLogicAttr[data-l1key=id]').value('');
      if (_options != '') {
        $("#div_configIncludeDevice").show();
        $('.eqLogicAttr[data-l1key=id]').value(_options);
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
        },
        dataType: 'json',
        error: function (request, status, error) {
            handleAjaxError(request, status, error);
        },
        success: function (data) { // si l'appel a bien fonctionné
        if (data.state != 'ok') {
            $('#div_inclusionAlert').showAlert({message: data.result, level: 'danger'});
            return;
        }
    }
});
}
