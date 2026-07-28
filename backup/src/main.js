// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import Vuex from 'vuex'
import store from './vuex/store'
// import ElementUI from 'element-ui'
// import 'element-ui/lib/theme-chalk/index.css'
import VueResource from 'vue-resource'
import echarts from 'echarts'
import Api from './api/index.js'

Vue.prototype.$api = Api
Vue.use(VueResource)
Vue.prototype.$echarts = echarts
Vue.use(Vuex)
// Vue.use(ElementUI)
Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  template: '<App/>',
  render: h => h(App),
  components: { App }
})
