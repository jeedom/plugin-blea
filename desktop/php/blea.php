<?php
if (!isConnect('admin')) {
	throw new Exception('Error 401 Unauthorized');
}
$plugin = plugin::byId('blea');
sendVarToJS('eqType', $plugin->getId());
$eqLogics = eqLogic::byType($plugin->getId());
function sortByOption($a, $b) {
	return strcmp($a['name'], $b['name']);
}
if (config::byKey('include_mode', 'blea', 0) == 1) {
	echo '<div class="alert jqAlert alert-warning" id="div_inclusionAlert" style="margin : 0px 5px 15px 15px; padding : 7px 35px 7px 15px;">{{Vous êtes en mode scan. Recliquez sur le bouton scan pour sortir de ce mode (sinon le mode restera actif une minute)}}</div>';
} else {
	echo '<div id="div_inclusionAlert"></div>';
}
?>

 <div class="col-lg-12 eqLogicThumbnailDisplay">
   <legend><i class="fas fa-cog"></i>  {{Gestion}}</legend>
   <div class="eqLogicThumbnailContainer">
    <?php
if (config::byKey('include_mode', 'blea', 0) == 1) {
	echo '<div class="cursor changeIncludeState include card logoPrimary" data-mode="1" data-state="0" >';
	echo '<i class="fa fa-spinner fa-pulse"></i>';
	echo '<br/>';
	echo '<span>{{Arrêter Scan}}</span>';
	echo '</div>';
} else {
	echo '<div class="cursor changeIncludeState include card logoPrimary " data-mode="1" data-state="1">';
	echo '<i class="fa fa-bullseye"></i>';
	echo '<br/>';
	echo '<span>{{Lancer Scan}}</span>';
	echo '</div>';
}
?>
   <div class="cursor eqLogicAction logoSecondary" data-action="gotoPluginConf">
      <i class="fas fa-wrench"></i>
	<br/>
    <span>{{Configuration}}</span>
  </div>
  <div class="cursor logoSecondary" id="bt_healthblea">
      <i class="fas fa-medkit"></i>
	<br/>
    <span>{{Santé}}</span>
  </div>
  <div class="cursor logoSecondary" id="bt_graphblea">
	<i class="fas fa-asterisk"></i>
	<br/>
	<span>{{Réseau}}</span>
	</div>
  <div class="cursor logoSecondary" id="bt_remoteblea">
	<i class="fab fa-bluetooth"></i>
	<br/>
	<span>{{Antennes}}</span>
	</div>
</div>
<legend><i class="fa fa-table"></i>  {{Mes devices Blea}}</legend>
<input class="form-control" placeholder="{{Rechercher}}" id="in_searchEqlogic" />
<div class="eqLogicThumbnailContainer">
  <?php
foreach ($eqLogics as $eqLogic) {
	$opacity = ($eqLogic->getIsEnable()) ? '' : 'disableCard';
	echo '<div class="eqLogicDisplayCard cursor '.$opacity.'" data-eqLogic_id="' . $eqLogic->getId() . '">';
	$alternateImg = $eqLogic->getConfiguration('iconModel');
	if (file_exists(dirname(__FILE__) . '/../../core/config/devices/' . $alternateImg . '.jpg')) {
		echo '<img class="lazy" src="plugins/blea/core/config/devices/' . $alternateImg . '.jpg"/>';
	} elseif (file_exists(dirname(__FILE__) . '/../../core/config/devices/' . $eqLogic->getConfiguration('device') . '.jpg')) {
		echo '<img class="lazy" src="plugins/blea/core/config/devices/' . $eqLogic->getConfiguration('device') . '.jpg"/>';
	} else {
		echo '<img src="' . $plugin->getPathImgIcon() . '"/>';
	}
	echo '<br/>';
	echo '<span class="name">' . $eqLogic->getHumanName(true, true) . '</span>';
	echo '</div>';
}
?>
</div>
</div>

<div class="col-lg-12 eqLogic" style="display: none;">
 <a class="btn btn-success eqLogicAction pull-right" data-action="save"><i class="fa fa-check-circle"></i> {{Sauvegarder}}</a>
 <a class="btn btn-danger eqLogicAction pull-right" data-action="remove"><i class="fa fa-minus-circle"></i> {{Supprimer}}</a>
 <a class="btn btn-default eqLogicAction pull-right" data-action="configure"><i class="fa fa-cogs"></i> {{Configuration avancée}}</a>
 <ul class="nav nav-tabs" role="tablist">
  <li role="presentation"><a href="#" class="eqLogicAction" aria-controls="home" role="tab" data-toggle="tab" data-action="returnToThumbnailDisplay"><i class="fa fa-arrow-circle-left"></i></a></li>
  <li role="presentation" class="active"><a href="#eqlogictab" aria-controls="home" role="tab" data-toggle="tab"><i class="fa fa-tachometer"></i> {{Equipement}}</a></li>
  <li role="presentation"><a href="#commandtab" aria-controls="profile" role="tab" data-toggle="tab"><i class="fa fa-list-alt"></i> {{Commandes}}</a></li>
</ul>
<div class="tab-content" style="height:calc(100% - 50px);overflow:auto;overflow-x: hidden;">
  <div role="tabpanel" class="tab-pane active" id="eqlogictab">
    <br/>
    <div class="row">
      <div class="col-sm-6">
        <form class="form-horizontal">
          <fieldset>
            <div class="form-group">
              <label class="col-sm-3 control-label">{{Nom du device}}</label>
              <div class="col-sm-4">
                <input type="text" class="eqLogicAttr form-control" data-l1key="id" style="display : none;" />
                <input type="text" class="eqLogicAttr form-control" data-l1key="name" placeholder="Nom de l'équipement BLEA"/>
              </div>
            </div>
            <div class="form-group">
              <label class="col-sm-3 control-label">{{Mac}}</label>
              <div class="col-sm-4">
                <input type="text" class="eqLogicAttr form-control" data-l1key="logicalId" placeholder="Logical ID"/>
              </div>
            </div>
            <div class="form-group">
              <label class="col-sm-3 control-label"></label>
              <div class="col-sm-9">
                <label class="checkbox-inline"><input type="checkbox" class="eqLogicAttr" data-l1key="isEnable" checked/>{{Activer}}</label>
                <label class="checkbox-inline"><input type="checkbox" class="eqLogicAttr" data-l1key="isVisible" checked/>{{Visible}}</label>
              </div>
            </div>
            <div class="form-group">
              <label class="col-sm-3 control-label">{{Objet parent}}</label>
              <div class="col-sm-4">
                <select class="eqLogicAttr form-control" data-l1key="object_id">
                  <option value="">Aucun</option>
                  <?php
foreach (object::all() as $object) {
	echo '<option value="' . $object->getId() . '">' . $object->getName() . '</option>';
}
?>
               </select>
             </div>
           </div>
           <div class="form-group">
            <label class="col-sm-3 control-label">{{Catégorie}}</label>
            <div class="col-sm-9">
              <?php
foreach (jeedom::getConfiguration('eqLogic:category') as $key => $value) {
	echo '<label class="checkbox-inline">';
	echo '<input type="checkbox" class="eqLogicAttr" data-l1key="category" data-l2key="' . $key . '" />' . $value['name'];
	echo '</label>';
}
?>

           </div>
         </div>
		 <div class="form-group">
				<label class="col-sm-3 control-label help" data-help="{{Antenne qui prendra les infos, attention ne pas mettre sur les devices de type boutons pour éviter la répétition des infos (sauf si c'est ce que vous souhaitez). Cependant presence et rssi sera systematiquement pris en compte par toutes les antennes.}}">{{Antenne de réception}}</label>
              <div class="col-sm-3">
                <select class="eqLogicAttr form-control" data-l1key="configuration" data-l2key="antennareceive">
                <option value="local">{{Local}}</option>
				<?php
				try{
					$hasblea = plugin::byId('blea');
					} catch (Exception $e) {
				}
				if ($hasblea != '' && $hasblea->isActive()){
					$remotes = blea_remote::all();
					foreach ($remotes as $remote) {
						echo '<option value="' . $remote->getId() . '">{{Remote : ' . $remote->getRemoteName() .'}}</option>';
					}
				}
				?>
				<option value="all">{{Tous}}</option>
              </select>
            </div>
			 <div class="form-group refreshdelay" style="display:none">
				<label class="col-sm-3 control-label help" data-help="{{Inutile de mettre des valeurs trop faible, si les valeurs sont identiques aux précédentes il n'y aura pas de mise à jour}}">{{Refresh des infos (en s)}}</label>
				<div class="col-sm-3">
				<input type="text" class="eqLogicAttr form-control" data-l1key="configuration" data-l2key="delay" placeholder="Delai en secondes"/>
				</div>
			</div>
			
		</div>
		<div class="form-group cancontrol" style="display:none">
				<label class="col-sm-3 control-label help" data-help="{{Utile pour savoir qu'elle antenne contrôllera l'équipement. Choisir tous aura la conséquence de déclencher potentiellement l'action autant de fois qu'il y a d'antennes}}">{{Antenne d'émission}}</label>
              <div class="col-sm-3">
                <select class="eqLogicAttr form-control" data-l1key="configuration" data-l2key="antenna">
                <option value="local">{{Local}}</option>
				<?php
				try{
					$hasblea = plugin::byId('blea');
					} catch (Exception $e) {
				}
				if ($hasblea != '' && $hasblea->isActive()){
					$remotes = blea_remote::all();
					foreach ($remotes as $remote) {
						echo '<option value="' . $remote->getId() . '">{{Remote : ' . $remote->getRemoteName() .'}}</option>';
					}
				}
				?>
				<option value="all">{{Tous}}</option>
              </select>
            </div>
			<div class="form-group canbelocked" style="display:none">
				<label class="col-sm-3 control-label help" data-help="{{Essaiera de garder la connection avec l'appareil (pour les appareils lent a se connecter). Attention une fois une connection ouverte certains appareils ne sont plus visibles. Si Tous est sélectionné cette option ne sera pas utilisé. Evitez absolument cette option sur des devices fonctionnant sur batterie}}">{{Garder la connection}}</label>
				<div class="col-sm-3">
				 <label class="checkbox-inline"><input type="checkbox" class="eqLogicAttr" data-l1key="configuration" data-l2key="islocked" />
				</div>
			</div>
          </div>
      </fieldset>
    </form>
  </div>
  <div class="col-sm-6">
    <form class="form-horizontal">
      <fieldset>
       <div class="form-group">
        <label class="col-sm-2 control-label"></label>
        <div class="col-sm-8">
          <a class="btn btn-danger" id="bt_autoDetectModule"><i class="fa fa-search" title="{{Recréer les commandes}}"></i>  {{Recréer les commandes}}</a>
		  <a class="btn btn-warning specificmodal" id="bt_specificmodal" style="display:none"><i class="fa fa-cogs"></i> {{Configuration spécifique}}</a>
          </div>
        </div>
     <div class="form-group">
      <label class="col-sm-2 control-label">{{Equipement}}</label>
      <div class="col-sm-8">
        <select class="eqLogicAttr form-control" data-l1key="configuration" data-l2key="device">
          <option value="">Aucun</option>
          <?php
$groups = array();
foreach (blea::devicesParameters() as $key => $info) {
	if (isset($info['groupe'])) {
		$info['key'] = $key;
		if (!isset($groups[$info['groupe']])) {
			$groups[$info['groupe']][0] = $info;
		} else {
			array_push($groups[$info['groupe']], $info);
		}
	}
}
ksort($groups);
foreach ($groups as $group) {
	usort($group, function ($a, $b) {
		return strcmp($a['name'], $b['name']);
	});
	foreach ($group as $key => $info) {
		if ($key == 0) {
			echo '<optgroup label="{{' . $info['groupe'] . '}}">';
		}
		echo '<option value="' . $info['key'] . '">' . $info['name'] . '</option>';
	}
	echo '</optgroup>';
}
?>
   </select>
 </div>
</div>
<div class="form-group modelList" style="display:none;">
  <label class="col-sm-2 control-label">{{Modèle}}</label>
  <div class="col-sm-8">
   <select class="eqLogicAttr form-control listModel" data-l1key="configuration" data-l2key="iconModel">
   </select>
 </div>
</div>

<center>
  <img src="core/img/no_image.gif" data-original=".jpg" id="img_device" class="img-responsive" style="max-height : 250px;"  onerror="this.src='plugins/openenocean/doc/images/openenocean_icon.png'"/>
</center>
</fieldset>
</form>
</br>
<div class="alert alert-info globalRemark" style="display:none"></div>
</div>
</div>

</div>
<div role="tabpanel" class="tab-pane" id="commandtab">
  <a class="btn btn-success btn-sm cmdAction pull-right" data-action="add" style="margin-top:5px;"><i class="fa fa-plus-circle"></i> {{Ajouter une commande}}</a><br/><br/>
  <table id="table_cmd" class="table table-bordered table-condensed">
    <thead>
      <tr>
        <th style="width: 300px;">{{Nom}}</th>
        <th style="width: 130px;">Type</th>
        <th>{{Logical ID (info) ou Commande brute (action)}}</th>
        <th>{{Paramètres}}</th>
        <th style="width: 100px;">{{Options}}</th>
        <th></th>
      </tr>
    </thead>
    <tbody>

    </tbody>
  </table>

</div>
</div>

</div>
</div>

<?php include_file('desktop', 'blea', 'js', 'blea');?>
<?php include_file('core', 'plugin.template', 'js');?>
