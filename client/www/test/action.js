module('Action', {
	setup : function() {
		this.mAction = new ActionImpl();
		Singleton().setHttpTransportClass(HttpTransportStub);
		ObserverStub.mParameters = new HashMap();
		ObserverStub.mLastActionId = "";
		ObserverStub.mLastSelect = SELECT_NONE;
		ObserverStub.mShow = false;
		ObserverStub.mTitle = "";

		ObserverFactoryMock.LastExtension = "";
		ObserverFactoryMock.LastAction = "";
		ObserverFactoryMock.LastParam = null;
	},
	teardown : function() {
		Singleton().close();
	}
});

test("Empty", function() {
	var action = {};
	this.mAction.initialize(null, null, action);

	equal(this.mAction.getTitle(), "", "Titre");
	equal(this.mAction.getExtension(), "", "Extension");
	equal(this.mAction.getAction(), "", "Action");
	equal(this.mAction.getIcon(), "", "Icon");
	equal(this.mAction.getFormType(), FORM_NOMODAL, "Modal");
	equal(this.mAction.getClose(), true, "Close");
	equal(this.mAction.getSelect(), SELECT_NONE, "Unique");
});

test("Action", function() {
	var action = {
		id : "CORE/usersEdit",
		modal : "1",
		icon : "/static/lucterios.CORE/images/edit.png",
		params : null,
		close : "0",
		text : "Modifier",
		action : "usersEdit",
		extension : "CORE",
		unique : "1"
	};
	this.mAction.initialize(null, null, action);
	equal(this.mAction.getTitle(), "Modifier", "Titre");
	equal(this.mAction.getID(), 'CORE/usersEdit', 'id');
	equal(this.mAction.getExtension(), "CORE", "Extension");
	equal(this.mAction.getAction(), "usersEdit", "Action");
	equal(this.mAction.getIcon(), "/static/lucterios.CORE/images/edit.png", "Icon");
	equal(this.mAction.getFormType(), FORM_MODAL, "Modal");
	equal(this.mAction.getClose(), false, "Close");
	equal(this.mAction.getSelect(), SELECT_NONE, "Unique");
	act_params = this.mAction.getParameters();
	equal(act_params.size(), 0, "params size");
});

test("Menu", function() {
	var act_params, action = {
		id : "CORE/usersEdit",
		modal : "0",
		icon : "",
		close : "1",
		text : "Modifier",
		action : "usersEdit",
		extension : "CORE",
		unique : "1",
		params : {
			'aaa' : '123',
			'bbb' : '546'
		}
	};
	this.mAction.initialize(null, null, action);

	equal(this.mAction.getID(), "CORE/usersEdit", "ID");
	equal(this.mAction.getTitle(), "Modifier", "Titre");
	equal(this.mAction.getExtension(), "CORE", "Extension");
	equal(this.mAction.getAction(), "usersEdit", "Action");
	equal(this.mAction.getIcon(), "", "Icon");
	equal(this.mAction.getFormType(), FORM_NOMODAL, "Modal");
	equal(this.mAction.getClose(), true, "Close");
	equal(this.mAction.getSelect(), SELECT_NONE, "Unique");
	act_params = this.mAction.getParameters();
	equal(act_params.size(), 2, "params size");
	equal(act_params.get('aaa'), '123', "params aaa");
	equal(act_params.get('bbb'), '546', "params bbb");
});

test("Simple", function() {
	var fact = new ObserverFactoryMock();
	ObserverFactoryMock.NewObserver = new ObserverStub();

	var action = {
		extension : 'CORE',
		action : 'changePassword',
		close : '0',
		modal : '1',
		text : 'Modifier',
		id : 'CORE/changePasword',
		icon : "",
		params : null,
	};
	this.mAction.initialize(null, fact, action);
	this.mAction.actionPerformed();

	equal(ObserverFactoryMock.LastExtension, "CORE", "extension");
	equal(ObserverFactoryMock.LastAction, "changePassword", "action");
	equal(ObserverFactoryMock.LastParam.size(), 0, "Params");
	ok(ObserverStub.mShow, "Show");
	equal(ObserverStub.mTitle, "Modifier", "Title");
	ok(ObserverFactoryMock.NewObserver.getGUI() == null, "GUI");
});

test("CloseParent", function() {
	var obs_parent = new ObserverStub();
	ObserverStub.mParameters.put("abc", "123");

	var fact = new ObserverFactoryMock();
	ObserverFactoryMock.NewObserver = new ObserverStub();

	var action = {
		extension : 'CORE',
		action : 'changePassword',
		close : '1',
		modal : '1',
		text : 'Modifier',
		id : 'CORE/changePasword',
		icon : "",
		params : null,
	};
	this.mAction.initialize(obs_parent, fact, action);
	this.mAction.actionPerformed();

	equal(ObserverFactoryMock.LastExtension, "CORE", "extension");
	equal(ObserverFactoryMock.LastAction, "changePassword", "action");
	equal(ObserverFactoryMock.LastParam.size(), 1, "Params");
	equal(ObserverFactoryMock.LastParam.get("abc"), "123", "Param 0");
	equal(this.mAction.getClose(), true, "Close");
	equal(this.mAction.getSelect(), SELECT_NONE, "Unique");
	ok(ObserverStub.mShow, "Show");
	equal(ObserverStub.mTitle, "Modifier", "Title");
	ok(ObserverFactoryMock.NewObserver.getParent() == null, "Parent");

	ok(obs_parent.mClose, "Close");
	equal(ObserverStub.mLastSelect, SELECT_NONE, "Select");
});

test("NoCloseParent", function() {
	var obs_parent = new ObserverStub();
	ObserverStub.mParameters.put("xyz", "456");
	ObserverStub.mParameters.put("ijk", "987");

	var fact = new ObserverFactoryMock();
	ObserverFactoryMock.NewObserver = new ObserverStub();

	var action = {
		extension : 'CORE',
		action : 'changePassword',
		close : '0',
		modal : '1',
		unique : '0',
		text : 'Modifier',
		id : 'CORE/changePasword',
		icon : "",
		params : null,
	};
	this.mAction.initialize(obs_parent, fact, action);
	this.mAction.actionPerformed();

	equal(ObserverFactoryMock.LastExtension, "CORE", "extension");
	equal(ObserverFactoryMock.LastAction, "changePassword", "action");
	equal(ObserverFactoryMock.LastParam.size(), 2, "Params");
	equal(ObserverFactoryMock.LastParam.get("xyz"), "456", "Param 0");
	equal(ObserverFactoryMock.LastParam.get("ijk"), "987", "Param 1");
	equal(this.mAction.getClose(), false, "Close");
	equal(this.mAction.getSelect(), SELECT_SINGLE, "Unique");
	ok(ObserverStub.mShow, "Show");
	equal(ObserverStub.mTitle, "Modifier", "Title");
	ok(ObserverFactoryMock.NewObserver.getParent() == obs_parent, "Parent");

	ok(!obs_parent.mClose, "Close");
});

test("OnlyCloseParent", function() {
	var obs_parent = new ObserverStub();
	ObserverStub.mParameters.put("abc", "123");

	var fact = new ObserverFactoryMock();
	ObserverFactoryMock.NewObserver = null;

	var action = {
		close : '1',
		modal : '0',
		text : 'Close',
		id : 'CORE/changePasword',
		icon : "",
		params : null,
	};
	this.mAction.initialize(obs_parent, fact, action);
	this.mAction.actionPerformed();

	equal(ObserverFactoryMock.LastExtension, "", "extension");
	equal(ObserverFactoryMock.LastAction, "", "action");
	equal(ObserverFactoryMock.LastParam, null, "Params");
	equal(this.mAction.getClose(), true, "Close");
	equal(this.mAction.getFormType(), FORM_NOMODAL, "Modal");
	equal(this.mAction.getSelect(), SELECT_NONE, "Unique");
	ok(!ObserverStub.mShow, "Show");
	equal(ObserverStub.mTitle, "", "Title");

	ok(obs_parent.mClose, "Close");
});
