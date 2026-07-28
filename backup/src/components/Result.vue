<template id="Result">
  <div id="Result">
    <p> <a style="font-size:1.90em;font-weight: bold">风险评估结果 </a></p>
    <p>实体名称：{{keyword}}</p>
    <div class="Grid">
    <div class="Grid1"><div class="item11"><view1></view1></div><div class="item11"><view2></view2></div><div  class="item11"><view3></view3></div></div>
    <div class="Grid2"><div class="item22"><a style="font-size:18px;font-weight:bold;">周边POI详情</a><map1></map1></div><div class="item22"><region></region></div><div class="item22"><category></category></div></div>
    <div class="Grid3"><div class="item33"><view4></view4></div><div class="item33"><info1></info1></div><div class="item33"><info3></info3></div><div class="item33"><info2></info2></div></div>
   </div></div>
</template>
<script type = "text/javascript" src = "http://api.map.baidu.com/api?v=2.0&ak=RIZ5gVBQ2k370IOE3oFGg8HNLaSHDwB2"></script>
<script>
export default {
  components: {
    view1: require("./view1.vue").default,
    view2: require("./view2.vue").default,
    view3: require("./view3.vue").default,
    view4: require("./view4.vue").default,
    info1: require("./info1.vue").default,
    info2: require("./info2.vue").default,
    info3: require("./info3.vue").default,
    map1: require("./map1.vue").default,
    region: require("./region.vue").default,
    category: require("./category.vue").default
  },
  computed: {
    keyword() {
      return this.$store.state.keyword;
    }
  }
};
</script>

<style>

.Grid1 {
  display: flex;
  flex-direction: row;
   justify-content: space-between;
  height: 400px;
}
.Grid1 item11 {
  flex-grow: 1
}
.Grid2 {
  display: flex;
  margin-bottom: 30px;
  flex-direction: row;
   justify-content: space-between;
  height: 400px;
}
.Grid2 item22{
  flex-grow:1
}
.Grid3 {
  display: flex;
  flex-direction: row;
   justify-content: space-between;
  height: 400px;
}
.Grid3 item33{
  flex-grow:1
}
</style>
