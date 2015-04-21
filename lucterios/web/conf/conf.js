/**
 * User: lag
 * Date: 26/11/13
 * Time: 13:49
 * Config unit for lucterios client
 */

var G_Version = '0.9.8.32';

var G_With_Extra_Menu = false;

var G_Active_Log = false;

function get_serverurl() {
    var fullurl=window.location.href;
    var n = fullurl.lastIndexOf("/");
    n = fullurl.substr(0,n).lastIndexOf("/");
    return fullurl.substr(0,n)+"/";
}

var AUTH_PARAM_NAME = ["username", "password", "ses", "info", "CORE"];

