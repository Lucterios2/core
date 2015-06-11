/*global ObserverAbstract,Singleton*/

var MODE_NONE = 0;
var MODE_PRINT = 1;
var MODE_PREVIEW = 2;
var MODE_EXPORT_PDF = 3;
var MODE_EXPORT_CSV = 4;

var ObserverPrint = ObserverAbstract
		.extend({
			mode : MODE_NONE,
			print_content : null,
			title : '',

			getObserverName : function() {
				return "CORE.Print";
			},

			setContent : function(aDomXmlContent) {
				this._super(aDomXmlContent);
				this.print_content = null;
				var print_elements = this.mDomXmlContent
						.getElementsByTagName("PRINT")[0];
				this.title = print_elements.getXMLAttributStr("title", "");
				this.title += print_elements.getCDataOfFirstTag("TITLE");
				this.mode = print_elements.getXMLAttributInt("mode",
						MODE_PREVIEW);
				this.print_content = print_elements.getTextFromXmlNode();
			},

			show : function(aTitle, aGUIType) {
				this._super(aTitle, aGUIType);

				var file_name = this.title.getFileNameWithoutForgottenChar();
				if (this.mode === MODE_EXPORT_CSV) {
					file_name += '.csv';
				} else {
					file_name += '.pdf';
				}

				Singleton().mFileManager
						.saveFile(this.print_content, file_name);
			}
		});
