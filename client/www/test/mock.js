var HttpTransportStub = HttpTransportAbstract.extend({
	JSONReceive : "",
	XmlParam : null,

	getIconUrl : function(icon) {
		return 'STUB/' + icon;
	},

	init : function() {
		this.XmlParam = new HashMap();
	},

	transfertFileFromServerString : function(aWebFile, aParams) {
		var self = this;
		this.XmlParam['WebFile'] = aWebFile;
		aParams.keys().forEach(function(key) {
			self.XmlParam[key] = decodeURIComponent(aParams.get(key));
		});
		return this.JSONReceive;
	},

	getFileContent : function(aUrl, callback) {
		this.XmlParam['URL'] = aUrl;
		var blob_content = null;
		if (typeof (Blob) === typeof (Function)) {
			blob_content = new Blob([ this.JSONReceive ], {
				type : "text/plain;charset=UTF-8"
			});
		} else {
			var builder = new WebKitBlobBuilder();
			builder.append(this.JSONReceive);
			blob_content = builder.getBlob();
		}
		callback(blob_content);
	},

});

var ObserverFactoryMock = ObserverFactoryAbstract.extend({
	CallList : new HashMap(),
	init : function() {
		this.CallList = new HashMap();
	},
	callAction : function(aExtension, aAction, aParam, aObserver) {
		var new_call, new_param = new HashMap();
		aParam.keys().forEach(function(key) {
			val = aParam.get(key);
			if (typeof val === 'string') {
				new_param[key] = val;
			}
		});
		new_call = "{0}->{1}({2})".format(aExtension, aAction, new_param.toString());
		this.CallList.put(this.CallList.size(), new_call);
		post_log('*** callAction:' + new_call);
		ObserverFactoryMock.LastExtension = aExtension;
		ObserverFactoryMock.LastAction = aAction;
		ObserverFactoryMock.LastParam = aParam;
		return ObserverFactoryMock.NewObserver;
	}
});
ObserverFactoryMock.LastExtension = "";
ObserverFactoryMock.LastAction = "";
ObserverFactoryMock.LastParam = null;
ObserverFactoryMock.NewObserver = null;

var ObserverStub = ObserverAbstract.extend({
	mClose : false,
	init : function() {
	},

	getObserverName : function() {
		return ObserverStub.ObserverName;
	},

	show : function(aTitle) {
		ObserverStub.mShow = true;
		ObserverStub.mTitle = aTitle;
	},

	getParameters : function(aCheckNull) {
		ObserverStub.mLastCheckNull = aCheckNull;
		return ObserverStub.mParameters;
	},

	close : function(aMustRefreshParent) {
		this.mClose = true;
		if (this.getGUI() != null)
			this.getGUI().setVisible(false);
		this._super(aMustRefreshParent);
	}

});
ObserverStub.ObserverName = "ObserverStub";
ObserverStub.mParameters = new HashMap();
ObserverStub.mLastCheckNull = false;
ObserverStub.mShow = false;
ObserverStub.mTitle = "";

var ObserverAcknowledgeNoParent = ObserverAcknowledge.extend({
	setParent : function(aParent) {
		this.mParent = null;
	},
});
