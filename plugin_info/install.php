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

require_once dirname(__FILE__) . '/../../../core/php/core.inc.php';

function blea_install() {
	$sql = file_get_contents(dirname(__FILE__) . '/install.sql');
	DB::Prepare($sql, array(), DB::FETCH_TYPE_ROW);
	foreach (blea::byType('blea') as $blea) {
		$blea->save();
	}
	config::save('version',blea::$_version,'blea');
}

function blea_update() {
	$sql = file_get_contents(dirname(__FILE__) . '/install.sql');
	DB::Prepare($sql, array(), DB::FETCH_TYPE_ROW);
	foreach (blea::byType('blea') as $blea) {
		$blea->save();
	}
	log::add('blea','alert','Pensez à mettre à jour vos antennes et relancer leurs dépendances si besoin ...');
	config::save('version',blea::$_version,'blea');
	if (config::bykey('allowUpdateAntennas','blea',0) == 1) {
		log::add('blea','alert','Mise à jour des fichiers de toutes les antennes');
		blea::send_allremotes();
	}
}

function blea_remove() {
	DB::Prepare('DROP TABLE IF EXISTS `blea_remote`', array(), DB::FETCH_TYPE_ROW);
}

?>
