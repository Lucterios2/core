/*global ObserverAbstract,Singleton*/

var MODE_NONE = 0;
var MODE_PRINT = 1;
var MODE_PREVIEW = 2;
var MODE_EXPORT_PDF = 3;
var MODE_EXPORT_CSV = 4;

var ObserverPrint = ObserverAbstract.extend({
	mode : MODE_NONE,
	print_content : null,
	title : '',

	getObserverName : function() {
		return "CORE.Print";
	},

	setContent : function(aJSON) {
		this._super(aJSON);
		this.print_content = null;
		var print_elements = this.mJSON.print;
		this.title = print_elements.title;
		this.mode = parseInt(print_elements.mode, 10) || MODE_PREVIEW;
		this.print_content = print_elements.content;
	},

	show : function(aTitle, aGUIType) {
		this._super(aTitle, aGUIType);

		var file_name = this.title.getFileNameWithoutForgottenChar();
		if (this.mode === MODE_EXPORT_CSV) {
			file_name += '.csv';
		} else {
			file_name += '.pdf';
		}

		Singleton().mFileManager.saveFile(this.print_content, file_name);
	}
});
