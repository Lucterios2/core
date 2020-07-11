/**
 * Config unit for lucterios Cordova (generic)
 */

function get_version() {
	var allText, rawFile = new XMLHttpRequest();
	rawFile.open("GET", "conf/build", false);
	rawFile.onreadystatechange = function() {
		if (rawFile.readyState === 4) {
			allText = rawFile.responseText;
		}
	}
	rawFile.send();
	return allText;
}

var G_With_Extra_Menu = false;

var G_Active_Log = false;

var G_Multi_Server = true;

function get_serverurl() {
	var current = get_servers_conf().current;
	if ((current !== null) && (current.slice(-1) !== '/')) {
		current = current + '/';
	}
	return current;
}
