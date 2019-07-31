<?php
require_once dirname(__FILE__) . "/../../../../../../../core/php/core.inc.php";
require_once dirname(__FILE__) . "/parsedown.php";

$docdir = dirname(__FILE__) . "/README.md";

$Parsedown = new Parsedown();

$markdown = file_get_contents($docdir);
echo $Parsedown->text($markdown);
