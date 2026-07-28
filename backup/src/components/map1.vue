<template id="map1">
<div id="map1" style="height:340px; width:370px ;margin-bottom:30px">
  
</div>
</template>

<script type="text/javascript" src="http://api.map.baidu.com/api?v=2.0&ak=RIZ5gVBQ2k370IOE3oFGg8HNLaSHDwB2"></script>
<script>
import {MP} from '../api/map1.js' 
export default {
    data () {
    return {
    }
  },
 mounted(){  
            this.$nextTick(function(){
             var key = this.$store.state.keyword   
          var map = new BMap.Map("map1")   
          map.centerAndZoom(new BMap.Point(116.404, 39.915), 11)   
          var local = new BMap.LocalSearch(map, {      
          renderOptions:{map: map}      
          })     
          local.search(key) 
  })}}
</script>

<style>
</style>
