'use strict';
var HTML_HEADER_TEMPLATE =
	'<nav class="navbar navbar-inverse navbar-fixed-top">'
    + ' <div class="container-fluid">'
    + '     <div class="lucterios-header">'
    + '         <button type="button" class="lucterios-menu">'
    + '             <span class="glyphicon glyphicon-menu-hamburger"></span>'
    + '         </button>'
	+ '	        <img class="logo" src="{0}">'
    + '         <a class="navbar-brand" href="#">{1}</a>'
    + '         <span class="connecteduser">{2}</span>'
    + '         <div class="header-right">'
    + '            <button type="button" id="BT_refresh">'
    + '                <span class="glyphicon glyphicon-refresh"></span>'
    + '                <span class="btn-last">{3}</span>'
    + '            </button>'
    + '            <button type="button" id="BT_about">'
    + '                <span class="glyphicon glyphicon-info-sign"></span>'
    + '                <span class="btn-last">{4}</span>'
    + '            </button>'
    + '            <button type="button" id="BT_help">'
    + '                <span class="glyphicon glyphicon-question-sign"></span>'
    + '                <span class="btn-last">{5}</span>'
    + '            </button>'
    + '            <button type="button" id="BT_logoff">'
    + '                <span class="glyphicon glyphicon-off"></span>'
    + '                <span class="btn-last">{6}</span>'
    + '            </button>'
    + '        </div>'
    + '    </div>'
    + '  </div>'
    + '</nav>';

var DIV_SUMMARY_TEMPLATE =
    '<div class="panel-heading" role="tab" id="summary_header">'
    + '    <h4 class="panel-title">'
    + '        <a class="collapsed" role="button" data-toggle="collapse" data-parent="#accordion" href="#summary_content" aria-expanded="true" aria-controls="summary_content">'
    + '            {0}'
    + '        </a>'
    + '        </h4>'
    + '    </div>'
    + '<div id="summary_content" class="panel-collapse collapse" role="tabpanel" aria-labelledby="summary_header">'
    + '    <div class="panel-body">'
    + '         {1}'
    + '    </div>'
    + '</div>';

var SIDE_MENU_BUTTON_TEMPLATE =
    '<li role="presentation" class="menu{0}">'
    + '<a href="#" class="switch-content" data="{1}">'
    + '<img src="{2}">{3}'
    + '</a></li>';

var CONTENT_MENU_MAIN_DIV_TEMPLATE = '<div id="{0}" class="content-container"></div>';
var CONTENT_MENU_INSIDE_PANEL_TEMPLATE =
    '<div class="panel panel-default" id="{0}">'
    + '    <div class="panel-heading"><h3 class="panel-title"><img src="{1}">{2}</h3></div>'
    + '    <div class="panel-body">'
    + '    </div>'
    + '</div>';
var CONTENT_MENU_BUTTON_TEMPLATE =
    '<button type="button" class="btn btn-default" id="BTCONTENT_{3}">'
    + '    <img src="{0}">{1}<br/>'
    + '    <span class="description">{2}</span>'
    + '</button>';

var MODAL_TEMPLATE =
    '<div class="modal fade" id="{0}" tabindex="-1" role="dialog" aria-labelledby="{0}_label">'
    + '  <div class="modal-dialog" role="document">'
    + '    <div class="modal-content">'
    + '      <div class="modal-header">'
    + '        <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>'
    + '        <h4 class="modal-title" id="{0}_label">{1}</h4>'
    + '      </div>'
    + '      <div class="modal-body">'
    + '        {2}'
    + '      </div>'
    + '      <div class="modal-footer">'
    + '        {3}'
    + '      </div>'
    + '    </div>'
    + '  </div>'
    + '</div>';


var BUTTON_TEMPLATE = '<button type="button" class="btn btn-default" id="BT_{0}_{1}">{2}</button>';


var LOGON_FORM_TEMPLATE =
    '<label style="width:100%;text-align:center;color:red;">{0}</label><br/>'
    + '<span style="width:95%;margin:5px;"><b>{1}</b></span>'
    + '<input name="username" id="logon_username" type="text" style="width:95%;margin:5px;"/><br/>'
    + '<span style="width:95%;margin:5px;"><b>{2}</b></span>'
    + '<input name="password" type="password" id="logon_password" style="width:95%;margin:5px;"/>';