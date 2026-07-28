import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

var store = new Vuex.Store({
  // 定义状态
  state: {
    keyword: '请输入要查询的机构实体',
    grade: 50,
    get: [],
    cha: 0
  }
 // ,
 // mutations: {
 //   a: state => { this.$store.state.grade = gra },
 //   b: state => { this.$store.state.get = getoptiondate },
 //   c: state => { this.$store.state.cha = change }
 // }
})

export default store
