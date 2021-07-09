import Vue from 'vue'
import { JSDOM } from 'jsdom'

Vue.config.productionTip = false

const dom = new JSDOM()
global.document = dom.window.document
global.window = dom.window
global.screen = { width: 800, height: 800, istest: true }
