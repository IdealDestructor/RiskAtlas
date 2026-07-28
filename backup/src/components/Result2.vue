<template id="Result2">
  <div>
    <p> <a style="font-size:1.90em;font-weight: bold">风险评估结果 </a></p>
    <p>地区/行业名称：{{keyword}}</p>
    <div class="div1"><table><tr><td><view1></view1></td><td> <view2></view2></td><td><view3></view3></td></tr></table></div>
    <div class="div2"><table><tr><td><region2></region2></td><td><category2></category2></td><td><view4></view4></td></tr></table></div>
    <div class="div3"><table><tr><td></td></tr></table></div>
   </div>
</template>
<script>
export default {
  components: {
    view1: require('./view1.vue').default,
    view2: require('./view2.vue').default,
    view3: require('./view3.vue').default,
    view4: require('./view4.vue').default,
    API1: require('./API1.vue').default,
    API2: require('./API2.vue').default,
    API3: require('./API3.vue').default,
    region2:require('./region2.vue').default,
    region1:require('./region1.vue').default,
    category1:require('./category1.vue').default,
    category2:require('./category2.vue').default
  },
  computed: {
    keyword () {
      return this.$store.state.keyword
    }
  }
}
</script>

<style>
.div1{margin:0px;
    width:100%
}
.div2{margin:0px;
    width:100%
}
.div3{margin-top:20px;
    width:100%
}

</style>