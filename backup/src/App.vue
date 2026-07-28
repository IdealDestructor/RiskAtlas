<template>
  <div id="app">
    <br/>
    <a href="http://yutu.idealdestructor.com"><img src="./assets/logo.png"></a>
    <router-view class="view"></router-view>
  </div>
</template>

<script>
import roof from './components/roof.vue'
import About from './components/About.vue'
import Result from './components/Result'
import Result2 from './components/Result2'
import search2 from './components/search2'
export default {
  components: { roof, Result, About, search2, Result2 }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 0px;
  margin-left: 0px
}
</style>
