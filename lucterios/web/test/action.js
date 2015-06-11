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
	var action = "<ACTION/>".parseXML();
	this.mAction.initialize(null, null, action);

	equal(this.mAction.getTitle(), "", "Titre");
	equal(this.mAction.getMnemonic(), 0, "Mnemonic");
	equal(this.mAction.getExtension(), "", "Extension");
	equal(this.mAction.getAction(), "", "Action");
	equal(this.mAction.getIcon(), "", "Icon");
	equal(this.mAction.getFormType(), FORM_NOMODAL, "Modal");
	equal(this.mAction.getClose(), true, "Close");
	equal(this.mAction.getSelect(), SELECT_NONE, "Unique");
});

test(
		"Action",
		function() {
			var action = "<ACTION icon='images/edit.png' extension='CORE' action='extension_params_APAS_modifier' close='0' modal='1' unique='1'><![CDATA[_Modifier]]></ACTION>"
					.parseXML();
			this.mAction.initialize(null, null, action);

			equal(this.mAction.getTitle(), "Modifier", "Titre");
			equal(this.mAction.getMnemonic(), 'M', "Mnemonic");
			equal(this.mAction.getExtension(), "CORE", "Extension");
			equal(this.mAction.getAction(), "extension_params_APAS_modifier",
					"Action");
			equal(this.mAction.getIcon(), "images/edit.png", "Icon");
			equal(this.mAction.getFormType(), FORM_MODAL, "Modal");
			equal(this.mAction.getClose(), false, "Close");
			equal(this.mAction.getSelect(), SELECT_NONE, "Unique");
		});

test(
		"Menu",
		function() {
			var action = "<MENU id='Im_pressionsauvegardees' extension='CORE' action='finalreport_APAS_list'><![CDATA[Im_pression sauvegardees]]></MENU>"
					.parseXML();
			this.mAction.initialize(null, null, action);

			equal(this.mAction.getID(), "Im_pressionsauvegardees", "ID");
			equal(this.mAction.getTitle(), "Impression sauvegardees", "Titre");
			equal(this.mAction.getMnemonic(), 'p', "Mnemonic");
			equal(this.mAction.getExtension(), "CORE", "Extension");
			equal(this.mAction.getAction(), "finalreport_APAS_list", "Action");
			equal(this.mAction.getIcon(), "", "Icon");
			equal(this.mAction.getFormType(), FORM_NOMODAL, "Modal");
			equal(this.mAction.getClose(), true, "Close");
			equal(this.mAction.getSelect(), SELECT_NONE, "Unique");
		});

test(
		"Simple",
		function() {
			var fact = new ObserverFactoryMock();
			ObserverFactoryMock.NewObserver = new ObserverStub();

			var action = "<ACTION extension='CORE' action='extension_params_APAS_modifier' close='0' modal='1'><![CDATA[_Modifier]]></ACTION>"
					.parseXML();
			this.mAction.initialize(null, fact, action);
			this.mAction.actionPerformed();

			equal(ObserverFactoryMock.LastExtension, "CORE", "extension");
			equal(ObserverFactoryMock.LastAction,
					"extension_params_APAS_modifier", "action");
			equal(ObserverFactoryMock.LastParam.size(), 0, "Params");
			ok(ObserverStub.mShow, "Show");
			equal(ObserverStub.mTitle, "Modifier", "Title");
			ok(ObserverFactoryMock.NewObserver.getGUI() == null, "GUI");
		});

test(
		"CloseParent",
		function() {
			var obs_parent = new ObserverStub();
			ObserverStub.mParameters.put("abc", "123");

			var fact = new ObserverFactoryMock();
			ObserverFactoryMock.NewObserver = new ObserverStub();

			var action = "<ACTION extension='CORE' action='extension_params_APAS_modifier' close='1' modal='1'><![CDATA[_Modifier]]></ACTION>"
					.parseXML();
			this.mAction.initialize(obs_parent, fact, action);
			this.mAction.actionPerformed();

			equal(ObserverFactoryMock.LastExtension, "CORE", "extension");
			equal(ObserverFactoryMock.LastAction,
					"extension_params_APAS_modifier", "action");
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

test(
		"NoCloseParent",
		function() {
			var obs_parent = new ObserverStub();
			ObserverStub.mParameters.put("xyz", "456");
			ObserverStub.mParameters.put("ijk", "987");

			var fact = new ObserverFactoryMock();
			ObserverFactoryMock.NewObserver = new ObserverStub();

			var action = "<ACTION extension='CORE' action='extension_params_APAS_modifier' close='0' modal='1' unique='0'><![CDATA[_Modifier]]></ACTION>"
					.parseXML();
			this.mAction.initialize(obs_parent, fact, action);
			this.mAction.actionPerformed();

			equal(ObserverFactoryMock.LastExtension, "CORE", "extension");
			equal(ObserverFactoryMock.LastAction,
					"extension_params_APAS_modifier", "action");
			equal(ObserverFactoryMock.LastParam.size(), 2, "Params");
			equal(ObserverFactoryMock.LastParam.get("xyz"), "456", "Param 0");
			equal(ObserverFactoryMock.LastParam.get("ijk"), "987", "Param 1");
			equal(this.mAction.getClose(), false, "Close");
			equal(this.mAction.getSelect(), SELECT_SINGLE, "Unique");
			ok(ObserverStub.mShow, "Show");
			equal(ObserverStub.mTitle, "Modifier", "Title");
			ok(ObserverFactoryMock.NewObserver.getParent() == obs_parent,
					"Parent");

			ok(!obs_parent.mClose, "Close");
		});

test("OnlyCloseParent", function() {
	var obs_parent = new ObserverStub();
	ObserverStub.mParameters.put("abc", "123");

	var fact = new ObserverFactoryMock();
	ObserverFactoryMock.NewObserver = null;

	var action = "<ACTION close='1' modal='0'><![CDATA[_Close]]></ACTION>"
			.parseXML();
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
