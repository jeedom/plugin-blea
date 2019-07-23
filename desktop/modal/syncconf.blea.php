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
?>
<div id='div_syncconfBleaAlert' style="display: none;"></div>
<a class="btn btn-warning pull-right" data-state="1" id="bt_bleaLogStopStart"><i class="fa fa-pause"></i> {{Pause}}</a>
<input class="form-control pull-right" id="in_bleaLogSearch" style="width : 300px;" placeholder="{{Rechercher}}"/>
<br/><br/><br/>
<pre id='pre_bleasyncconf' style='overflow: auto; height: 90%;with:90%;'>
Arrêt du démon en cours
</pre>

<script>
    $.ajax({
        type: 'POST',
        url: 'plugins/blea/core/ajax/blea.ajax.php',
        data: {
            action: 'syncconfBlea',
        },
        dataType: 'json',
        global: false,
        error: function (request, status, error) {
            handleAjaxError(request, status, error, $('#div_syncconfBleaAlert'));
        },
        success: function () {
        }
    });
function updatelog(){
    jeedom.log.autoupdate({
                log: 'blea_syncconf',
                display: $('#pre_bleasyncconf'),
                search: $('#in_bleaLogSearch'),
                control: $('#bt_bleaLogStopStart'),
            });
}
setTimeout(updatelog,2000);
</script>