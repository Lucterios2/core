/*global $,Class, ObserverCustom, Singleton, FORM_MODAL, SELECT_NONE*/

function get_servers_conf() {
	var server_size, server_idx, server_value, servers_conf = {
		current : null,
		list : {}
	};
	servers_conf.current = localStorage.getItem('current_server');
	server_size = localStorage.getItem('current_nb');
	if (server_size !== null) {
		server_size = parseInt(server_size, 10);
		for (server_idx = 0; server_idx < server_size; server_idx++) {
			server_value = localStorage.getItem('server_{0}'.format(server_idx));
			if (server_value !== null) {
				server_value = server_value.split('|');
				servers_conf.list[server_value[0]] = server_value[1];
				if (servers_conf.current === null) {
					servers_conf.current = server_value[1];
				}
			}
		}
	}
	return servers_conf;
}

function set_servers_list(servers_conf) {
	/*jslint regexp: true*/
	var server_name, server_idx = 0, server_url_mask = new RegExp("^https?:\/\/[a-z0-9\/:%_+.,#?!@&=-]+$", 'i'), server_name_mask = new RegExp(
			"^[a-z0-9_\\-]+$", 'i');
	/*jslint regexp: false*/
	localStorage.clear();
	for (server_name in servers_conf.list) {
		if (servers_conf.list.hasOwnProperty(server_name) && server_name_mask.test(server_name)
				&& server_url_mask.test(servers_conf.list[server_name])) {
			localStorage.setItem('server_{0}'.format(server_idx), "{0}|{1}".format(server_name, servers_conf.list[server_name]));
			if (servers_conf.current === null) {
				servers_conf.current = servers_conf.list[server_name];
			}
			server_idx = server_idx + 1;
		}
	}
	localStorage.setItem("current_nb", "{0}".format(server_idx));
	localStorage.setItem("current_server", servers_conf.current);
}

var ServerManager = Class.extend({

	create_gui : function(title, modal, json_content) {
		var comp_idx, action_idx, comp;
		this.mObs = new ObserverCustom();
		this.mObs.setSource('', '');
		this.mObs.setContent(json_content);
		this.mObs.show(title, modal);
		if (json_content.close !== undefined) {
			this.mObs.mGUI.defaultbtn.callback = $.proxy(json_content.close.callback, this);
		}
		for (comp_idx = 0; comp_idx < json_content.comp.length; comp_idx++) {
			comp = json_content.comp[comp_idx];
			if (comp.actions !== undefined) {
				for (action_idx = 0; action_idx < comp.actions.length; action_idx++) {
					this.mObs.mCompList[comp.name].buttons[action_idx].btnaction.callback = $.proxy(comp.actions[action_idx].callback, this);
				}
			}
		}
		for (action_idx = 0; action_idx < json_content.actions.length; action_idx++) {
			this.mObs.mGUI.mButtons[action_idx].callback = $.proxy(json_content.actions[action_idx].callback, this);
		}
		this.mObs.mGUI.mButtons[json_content.actions.length - 1].mCheckNull = false;
		$("#refresh_" + this.mObs.mGUI.mId).parent().find('.ui-dialog-titlebar-close').remove();
		$("#refresh_" + this.mObs.mGUI.mId).remove();
		$("#fullscreen_" + this.mObs.mGUI.mId).remove();
	},

	add : function() {
		var json_content = {};
		json_content = {
			comp : [ {
				name : 'image',
				x : 0,
				y : 0,
				rowspan : 4,
				component : "IMAGE",
				type : ''
			}, {
				name : 'title',
				x : 1,
				y : 1,
				colspan : 3,
				component : "LABEL",
				formatstr : "{[center]}{[b]}{[u]}{0}{[/u]}{[/b]}{[/center]}",
				needed : true
			}, {
				name : 'name',
				x : 1,
				y : 2,
				component : "EDIT",
				description : Singleton().getTranslate('name'),
				reg_expr : "^[a-z0-9_\\-]+$",
				needed : true
			}, {
				name : 'url',
				x : 1,
				y : 3,
				component : "EDIT",
				description : Singleton().getTranslate("address"),
				reg_expr : "^https?:\/\/[a-z0-9\/:%_+.,#?!@&=-]+$",
				needed : true
			} ],
			data : {
				image : 'images/status.png',
				title : Singleton().getTranslate('Add new server address'),
				name : '',
				url : ''
			},
			close : {
				callback : this.show
			},
			actions : [ {
				text : Singleton().getTranslate('Ok'),
				modal : FORM_MODAL,
				close : '1',
				unique : SELECT_NONE,
				extension : 'server',
				action : 'save',
				id : 'server/save',
				params : null,
				callback : this.save,
				icon : 'images/ok.png'

			}, {
				text : Singleton().getTranslate('Close'),
				modal : FORM_MODAL,
				close : '1',
				unique : SELECT_NONE,
				params : null,
				callback : this.show,
				icon : 'images/close.png'
			} ]
		};
		this.create_gui(Singleton().getTranslate("Add server"), FORM_MODAL, json_content);
	},

	save : function(aParam) {
		var servers_conf = get_servers_conf();
		servers_conf.list[aParam.name] = aParam.url;
		set_servers_list(servers_conf);
		this.show();
	},

	delete_item : function(aParam) {
		var servers_conf = get_servers_conf();
		if (servers_conf.list[aParam.server] !== undefined) {
			delete servers_conf.list[aParam.server];
		}
		set_servers_list(servers_conf);
		this.show();
	},

	current_item : function(aParam) {
		var servers_conf = get_servers_conf();
		if (servers_conf.list[aParam.server] !== undefined) {
			servers_conf.current = servers_conf.list[aParam.server];
		}
		set_servers_list(servers_conf);
		this.show();
	},

	show : function() {
		var json_content, server_name, grid_content = {}, servers_conf = get_servers_conf();
		grid_content.x = 1;
		grid_content.y = 2;
		grid_content.name = 'server';
		grid_content.component = 'GRID';
		grid_content.no_pager = true;
		grid_content.headers = [ [ 'name', Singleton().getTranslate('name'), '', 0, '' ], [ 'url', Singleton().getTranslate('address'), '', 0, '' ],
				[ 'current', Singleton().getTranslate('current'), 'B', 0, '' ] ];
		grid_content.actions = [ {
			text : Singleton().getTranslate('current'),
			modal : FORM_MODAL,
			close : "1",
			unique : "0",
			icon : 'images/default.png',
			extension : 'server',
			action : 'current',
			id : 'server/current',
			params : null,
			callback : this.current_item
		}, {
			text : Singleton().getTranslate('add'),
			modal : FORM_MODAL,
			close : "1",
			unique : "1",
			extension : 'server',
			action : 'add',
			icon : 'images/add.png',
			id : 'server/add',
			params : null,
			callback : this.add
		}, {
			text : Singleton().getTranslate('delete'),
			modal : FORM_MODAL,
			close : "1",
			unique : "0",
			extension : 'server',
			action : 'delete',
			icon : 'images/delete.png',
			id : 'server/delete',
			params : null,
			callback : this.delete_item
		} ];
		json_content = {
			comp : [ {
				name : 'image',
				x : 0,
				y : 0,
				rowspan : 4,
				component : "IMAGE",
				type : ''
			}, {
				name : 'title',
				x : 1,
				y : 1,
				component : "LABEL",
				formatstr : "{[center]}{[b]}{[u]}{0}{[/u]}{[/b]}{[/center]}"
			}, grid_content ],
			data : {
				image : 'images/status.png',
				title : Singleton().getTranslate('Manage server addresses'),
				server : []
			},
			close : {
				callback : this.reload
			},
			actions : [ {
				text : Singleton().getTranslate('Ok'),
				modal : FORM_MODAL,
				close : 1,
				unique : SELECT_NONE,
				params : null,
				callback : this.reload,
				icon : 'images/ok.png'
			} ]

		};
		for (server_name in servers_conf.list) {
			if (servers_conf.list.hasOwnProperty(server_name)) {
				json_content.data.server.push({
					id : server_name,
					name : server_name,
					url : servers_conf.list[server_name],
					current : (servers_conf.list[server_name] === servers_conf.current)
				});
			}
		}
		this.create_gui(Singleton().getTranslate("Servers"), FORM_MODAL, json_content);
	}
});
