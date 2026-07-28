<template>
  <div id="view4" style="width:350px; height:500px; overflow:auto">
    <a>数据来源及摘要：</a>
  </div>
</template>

<script>
import jQuery from 'jquery'
import { getAddr } from '../addresses'
export default {
  name: 'bar-chart',
  data () {
    return {
    }
  },
  mounted () {
    this.$nextTick(function () {
      this.drawBarChart()
    })
  },
  methods: {
    drawBarChart () {
      var that = this
      var key = this.$store.state.keyword
      var obj = {}
      var result1 = []
      jQuery.ajax({
        type: 'post',
        async: false,
        url: getAddr('/servlet/helloWorld'),
        data: {keyword: key},
        dataType: 'json',
        success: function (result) {
          if (result) {
            for(var k = 0; k < result.length; k++){
             if(!obj[result[k].title,result[k].name]){ //如果能查找到，证明数组元素重复了
                obj[result[k].title,result[k].name] = 1
                result1.push(result[k])
              }
            }
            for (var i = 0; i < result1.length; i++) {
              var geturl = []
              var gettitle = []
              var getdigest = []
              geturl.push(result1[i].url)
              gettitle.push(result1[i].title)
              getdigest.push(result1[i].digest)
              let tr = document.createElement('tr')
              tr.innerHTML = '<br><a href = "' + geturl + '">' + gettitle + '</a>'
              let tr2 = document.createElement('tr')
              tr2.innerHTML = '<a>' + getdigest + '</a>'
              document.getElementById('view4').appendChild(tr)
              document.getElementById('view4').appendChild(tr2)
            }
          }
        }
      })
    }
  }
}
</script>

<style>
</style>