import Vue from 'vue'
import Router from 'vue-router'
import roof from '@/components/roof'
import About from '@/components/About'
import Result from '@/components/Result'
import Result2 from '@/components/Result2'
import search2 from '@/components/search2'


Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'roof',
      component: roof
    },
    {
      path: '/About',
      name: 'About',
      component: About
    },
    {
      path: '/Result',
      name: 'Result',
      component: Result
    },
    {
      path: '/search2',
      name: 'search2',
      component: search2
    },
    {
      path: '/Result2',
      name: 'Result2',
      component: Result2
    }
  ]
})
