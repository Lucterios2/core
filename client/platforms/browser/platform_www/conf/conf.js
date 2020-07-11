/**
 * Config unit for lucterios Cordova (browser)
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

var G_Multi_Server = false;

function get_serverurl() {
	var fullurl = window.location.href;
	var n = fullurl.lastIndexOf("/");
	n = fullurl.substr(0, n).lastIndexOf("/");
	return fullurl.substr(0, n) + "/";
}
