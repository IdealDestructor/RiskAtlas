<template id="API2">
  <div id="API2" style="width:600px; height:300px">
       <div id="API22" style="width:200px; height:300px"></div>
 <div id="API21" style="width:300px; height:300px">  
  </div>
  </div>
</template>

<script>
import jQuery from 'jquery'
import axios from 'axios'
import { getAddr } from '../addresses'
export default {
  data () {
    return {
    }
  },
  mounted () {
    this.$nextTick(function () {
      this.getinfo()
    })
  },
  methods: {
    getinfo () { 
    var key = this.$store.state.keyword
    var toke=""
        var keyreg = key.substring(0,2)
        var that = this
        var myChart = that.$echarts.init(document.getElementById('API21'))
        var result1= []
        var obj = {}
        var obj1={}
        var reg=[]
        var da=[]

        jQuery.ajax({
        type: 'post',
        async: false,
        url: getAddr('/servlet/helloWorld'),
        data: {keyword: keyreg},
        dataType: 'json',
        success: function (result) {
          if (result) {
            for(var k = 0; k < result.length; k++){
              if(!obj[result[k].title,result[k].name]){ //如果能查找到，证明数组元素重复了
                obj[result[k].title,result[k].name] = 1
                result1.push(result[k])
              }
            }
            for(var p = 0; p < result1.length; p++){
              if(!obj1[result1[p].name]){ //如果能查找到，证明数组元素重复了
                obj1[result1[p].name] = 1
                reg.push(result1[p].name)
              }
            }
            for (var q = 0; q < reg.length; q++) {
            var go=2
            var ba=2
            var si=2
            for (var i = 0; i < result1.length; i++) {
              if(result1[i].name === reg[q]){
                if (result1[i].eventLevel === '正向') {
                go+=3
                } else if (result1[i].eventLevel === '负向') {
                ba+=3
                } else
                {
                si+=3
                }
              }
            }
            go+=q
            ba+=q
            si+=q
            da[q]=[]
            da[q].push(go)
            da[q].push(si)
            da[q].push(ba)
            console.log(da[q])
            }
          }
        }
      })
      setTimeout(() => {
    myChart.setOption({
    title : {
        text: '本地区代表性企业舆情监测',
        x:'center'
    },
    tooltip : {
        trigger: 'item',
        formatter: "{a} <br/>{b} : {c} ({d}%)"
    },
    legend: {
        orient : 'vertical',
        x : 'left',
        data:reg
    },
    calculable : true,
    series : [
        {
            name:'总体情况',
            type:'pie',
            radius : '55%',
            center: ['50%', 225],
            data:[
                {value:335, name:'正向'},
                {value:310, name:'中性'},
                {value:434, name:'负向'},
            ]
        }
    ]
});
myChart2 = that.$echarts.init(document.getElementById('API22'));
setTimeout(() => {myChart2.setOption({
    tooltip : {
        trigger: 'axis',
        axisPointer : {
            type: 'shadow'
        }
    },
    legend: {
        data:reg
    },
    toolbox: {
        show : true,
        orient : 'vertical',
        y : 'center',
        feature : {
            mark : {show: true},
            magicType : {show: true, type: ['line', 'bar', 'stack', 'tiled']},
            restore : {show: true},
            saveAsImage : {show: true}
        }
    },
    calculable : true,
    xAxis : [
        {
            type : 'category',
            data :reg
        }
    ],
    yAxis : [
        {
            type : 'value',
            splitArea : {show : true}
        }
    ],
    grid: {
        x2:40
    },
    series : (function (){
        var series = [];
        for (var i = 1; i <= reg.length; i++) {
            series.push({
                name:reg[i],
                type:'bar',
                stack: '分布',
                data:da[i]
            })
        }
        return series;
    })()})
}, 2000)},2000)}}}
</script>
<style></style>