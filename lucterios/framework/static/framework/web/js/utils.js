/*global Class,String,Element,LucteriosException,CRITIC,DOMParser,ActiveXObject,G_Active_Log,console*/

var __next_objid = 1;

function createGuid() {
	return __next_objid++;
	/*
	 * return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,
	 * function(c) { var r = Math.random()*16|0, v = c === 'x' ? r :
	 * (r&0x3|0x8); return v.toString(16); });
	 */
}

function unusedVariables() {
	return undefined;
}

if (!String.prototype.format) {
	String.prototype.format = function() {
		var args = arguments;
		return this.replace(/\{(\d+)\}/g, function(match, number) {
			return args[number] !== undefined ? args[number] : match;
		});
	};
}

String.prototype.lpad = function(padString, length) {
	var str = this;
	while (str.length < length) {
		str = padString + str;
	}
	return str;
};

String.prototype.rpad = function(padString, length) {
	var str = this;
	while (str.length < length) {
		str = str + padString;
	}
	return str;
};

String.prototype.trim = function() {
	return this.replace(/^\s+|\s+$/g, "");
};

String.prototype.parseXML = function() {
	var xml_text, parser, xmlDoc, errorMsg;
	if (this.substr(0, 6) !== '<?xml ') {
		xml_text = '<?xml version="1.0" encoding="UTF-8"?>' + this;
	} else {
		xml_text = this;
	}
	if (window.DOMParser) {
		parser = new DOMParser();
		xmlDoc = parser.parseFromString(xml_text, "text/xml");
	} else { // Internet Explorer
		xmlDoc = new ActiveXObject("Microsoft.XMLDOM");
		xmlDoc.async = false;
		xmlDoc.loadXML(xml_text);
	}
	if (xmlDoc.parseError && xmlDoc.parseError.errorCode !== 0) {
		errorMsg = "XML Parsing Error: " + xmlDoc.parseError.reason
				+ " at line " + xmlDoc.parseError.line + " at position "
				+ xmlDoc.parseError.linepos;
		throw new LucteriosException(CRITIC, errorMsg);
	}
	return xmlDoc.documentElement;
};

var FORGOTTEN_CHAR = ":/\\<>| \"'";

String.prototype.getFileNameWithoutForgottenChar = function() {
	var new_text = this;
	new_text = new_text.replace(/:/g, '_');
	new_text = new_text.replace(/\//g, '_');
	new_text = new_text.replace(/\\/g, '_');
	new_text = new_text.replace(/</g, '_');
	new_text = new_text.replace(/>/g, '_');
	new_text = new_text.replace(/\|/g, '_');
	new_text = new_text.replace(/ /g, '_');
	new_text = new_text.replace(/"/g, '_');
	new_text = new_text.replace(/'/g, '_');
	return new_text.trim();
};

var HashMap = Class.extend({
	put : function(key, value) {
		this[key] = value;
	},
	get : function(key) {
		if (this[key] === undefined) {
			return null;
		}
		return this[key];
	},
	val : function(index) {
		var cursor = 0, prop;
		for (prop in this) {
			if (this.hasOwnProperty(prop) && (this[prop] !== undefined)) {
				if (cursor === index) {
					return this.get(prop);
				}
				cursor++;
			}
		}
		return null;
	},
	keys : function() {
		var result = [], prop;
		for (prop in this) {
			if (this.hasOwnProperty(prop) && (this[prop] !== undefined)) {
				result.push(prop);
			}
		}
		return result;
	},
	size : function() {
		var count = 0, prop;
		for (prop in this) {
			if (this.hasOwnProperty(prop)) {
				count++;
			}
		}
		return count;
	},
	putAll : function(aOtherMap) {
		var self = this;
		aOtherMap.keys().forEach(function(key) {
			self.put(key, aOtherMap[key]);
		});
	},

	toString : function() {
		var result = '', prop;
		for (prop in this) {
			if (this.hasOwnProperty(prop) && (this[prop] !== undefined)) {
				result += "{0}='{1}',".format(prop, this[prop]);
			}
		}
		return result;
	}
});

var FAILURE = 0;
var CRITIC = 1;
var GRAVE = 2;
var IMPORTANT = 3;
var MINOR = 4;

var LucteriosException = Class.extend({
	message : '',
	info : '',
	extra : '',
	init : function(aType, aMessage, aInfo, aExtra) {
		this.type = aType;
		this.message = aMessage;
		this.info = aInfo;
		this.extra = aExtra;
	},
	toString : function() {
		var res = this.type + '~' + this.message;
		if (this.info) {
			res += '#' + this.info;
			if (this.extra) {
				res += '#' + this.extra;
			}
		}
		return res;
	}
});

Element.prototype.getTextFromXmlNode = function() {
	var res = "", node_idx;
	for (node_idx = 0; node_idx < this.childNodes.length; node_idx++) {
		if ((this.childNodes[node_idx].nodeType === 3)
				|| (this.childNodes[node_idx].nodeType === 4)) {
			res += this.childNodes[node_idx].nodeValue;
		}
	}
	return res;
};

Element.prototype.getXMLAttributInt = function(aAttribName, aDefault) {
	var attr = this.getAttribute(aAttribName), val;
	if (attr === null) {
		return aDefault;
	}
	val = parseInt(attr, 10);
	if (isNaN(val)) {
		val = aDefault;
	}
	return val;
};

Element.prototype.getXMLAttributFloat = function(aAttribName, aDefault) {
	var attr = this.getAttribute(aAttribName), val;
	if (attr === null) {
		return aDefault;
	}
	val = parseFloat(attr);
	if (isNaN(val)) {
		val = aDefault;
	}
	return val;
};

Element.prototype.getXMLAttributStr = function(aAttribName, aDefault) {
	var attr = this.getAttribute(aAttribName);
	if (attr === null) {
		return aDefault;
	}
	return attr;
};

Element.prototype.getFirstTag = function(aTagName) {
	var item_idx, current_node;
	for (item_idx = 0; item_idx < this.childNodes.length; item_idx++) {
		current_node = this.childNodes[item_idx];
		if (current_node.tagName === aTagName) {
			return current_node;
		}
	}
	return null;
};

Element.prototype.getCDataOfFirstTag = function(aTagName) {
	var first_node = this.getFirstTag(aTagName);
	if (first_node) {
		return first_node.getTextFromXmlNode();
	}
	return '';
};

function post_log(aText) {
	if (G_Active_Log) {
		console.log(aText);
	}
}
