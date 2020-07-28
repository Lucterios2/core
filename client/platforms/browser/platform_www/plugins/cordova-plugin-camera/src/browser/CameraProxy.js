cordova.define("cordova-plugin-camera.CameraProxy", function(require, exports, module) { /*
 *
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 *
 */

	var HIGHEST_POSSIBLE_Z_INDEX = 2147483647;

	function takePicture(success, error, opts) {
		if (opts && opts[2] === 1) {
			capture(success, error, opts);
		} else {
			var input = document.createElement('input');
			input.style.position = 'relative';
			input.style.zIndex = HIGHEST_POSSIBLE_Z_INDEX;
			input.className = 'cordova-camera-select';
			input.type = 'file';
			input.name = 'files[]';

			input.onchange = function(inputEvent) {
				var reader = new FileReader(); /* eslint no-undef : 0 */
				reader.onload = function(readerEvent) {
					input.parentNode.removeChild(input);

					var imageData = readerEvent.target.result;

					return success(imageData.substr(imageData.indexOf(',') + 1));
				};

				reader.readAsDataURL(inputEvent.target.files[0]);
			};

			document.body.appendChild(input);
		}
	}

	function capture(success, errorCallback, opts) {
		var localMediaStream;
		var targetWidth = opts[3];
		var targetHeight = opts[4];

		targetWidth = targetWidth === -1 ? 320 : targetWidth;
		targetHeight = targetHeight === -1 ? 240 : targetHeight;

		var video = document.createElement('video');
		var parent = document.createElement('div');
		parent.style.position = 'relative';
		parent.style.zIndex = HIGHEST_POSSIBLE_Z_INDEX;
		parent.className = 'cordova-camera-capture';
		parent.appendChild(video);

		video.width = targetWidth;
		video.height = targetHeight;

		button_onclick = function() {
			// create a canvas and capture a frame from video stream
			var canvas = document.createElement('canvas');
			canvas.width = targetWidth;
			canvas.height = targetHeight;
			canvas.getContext('2d').drawImage(video, 0, 0, targetWidth, targetHeight);

			// convert image stored in canvas to base64 encoded image
			var imageData = canvas.toDataURL('image/png');
			imageData = imageData.replace('data:image/png;base64,', '');

			// stop video stream, remove video and button.
			// Note that MediaStream.stop() is deprecated as of Chrome 47.
			if (localMediaStream.stop) {
				localMediaStream.stop();
			} else {
				localMediaStream.getTracks().forEach(function(track) {
					track.stop();
				});
			}
			return success(imageData);
		};

		navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;

		var successCallback = function(stream) {
			var div_camera_capture;
			localMediaStream = stream;
			if ('srcObject' in video) {
				video.srcObject = localMediaStream;
			} else {
				video.src = window.URL.createObjectURL(localMediaStream);
			}
			video.play();
			document.body.appendChild(parent);
			div_camera_capture = $("div.cordova-camera-capture");
			div_camera_capture.dialog({
				title : Singleton().getTranslate("Take picture"),
				width : 'auto',
				height : 'auto',
				modal : true,
				classes : {
					"ui-dialog" : "lct-dialog",
					"ui-dialog-content" : "lct-dlgcontent",
					"ui-dialog-buttonpane" : "lct-dlgbtnpn",
					"ui-dialog-buttonset" : "lct-dlgbtnset"
				},
				buttons : [ {
					text : Singleton().getTranslate("Ok"),
					click : button_onclick
				}, {
					text : Singleton().getTranslate("Close"),
					click : errorCallback
				} ],
				close : errorCallback
			});
			btn = div_camera_capture.parent().find("div > div.lct-dlgbtnset > button:eq(0)");
			btn.prepend('<img height="24px" src="{0}" />'.format(Singleton().Transport().getIconUrl('static/lucterios.CORE/images/ok.png')));
			btn = div_camera_capture.parent().find("div > div.lct-dlgbtnset > button:eq(1)");
			btn.prepend('<img height="24px" src="{0}" />'.format(Singleton().Transport().getIconUrl('static/lucterios.CORE/images/close.png')));
		};

		if (navigator.getUserMedia) {
			navigator.getUserMedia({
				video : true,
				audio : false
			}, successCallback, errorCallback);
		} else {
			alert_function(Singleton().getTranslate('Browser does not support camera for this address :('));
		}
	}

	module.exports = {
		takePicture : takePicture,
		cleanup : function() {
		}
	};

	require('cordova/exec/proxy').add('Camera', module.exports);

});
