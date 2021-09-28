/**
 * Config unit for lucterios Cordova (generic)
 */

window.setVersionFct(function () {
  var allText
  var rawFile = new XMLHttpRequest()
  rawFile.open('GET', 'conf/build', false)
  rawFile.onreadystatechange = function () {
    if (rawFile.readyState === 4) {
      allText = rawFile.responseText
    }
  }
  rawFile.send()
  return allText
})

window.setServerUrl(function () {
  var fullurl = window.location.href
  var n = fullurl.lastIndexOf('/')
  n = fullurl.substr(0, n).lastIndexOf('/')
  return fullurl.substr(0, n) + '/'
})

window.setGlobalParam(true, false, false)
