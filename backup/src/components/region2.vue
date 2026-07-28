<template id="region2">
  <div id="region2" class="box" style="width:450px; height:400px">
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
        var myChart = that.$echarts.init(document.getElementById('region2'))
        myChart.showLoading()
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
    color :['#98FB98','#FFFAFA','#00FFFF','#00CED1','#87CEFA','#87CEEB','#00BFFF','#1E90FF','#F0FFF0','#836FFF','#9B30FF','#B0E2FF','#90EE90','#EE30A7','#F0FFF0','	#FF7F00'],  //(function (){
        //var zrColor = require('zrender/src/tool/color');
       // return zrColor.getStepColors('yellow', 'red', 28);
       //return zrColor.color.lerp(0.5, ['yellow', 'red'], false)
    //})(),
    title : {
        text: '同地区机构舆情',
        subtext: '分布监控雷达图',
        x:'right',
        y:'top'
    },
    tooltip : {
        trigger: 'item',
        backgroundColor : 'rgba(0,0,250,0.2)'
    },
    legend: {
        orient : 'vertical',
        x : 'left',
        data: reg
    },
    toolbox: {
        show : true,
        orient : 'vertical',
        y:'center',
        feature : {
            mark : {show: true},
            dataView : {show: true, readOnly: false},
            restore : {show: true},
            saveAsImage : {show: true}
        }
    },
   polar : [
       {
           indicator : [
               { text: '正向', max: 20},
               { text: '中性', max: 20},
               { text: '负向', max: 20}
            ],
            center : ['50%', 240],
            radius : 150
        }
    ],
    calculable : false,
    series : (function (){
        var series = [];
        for (var i = 1; i <= reg.length; i++) {
            series.push({
                type:'radar',
                symbol:'none',
                itemStyle: {
                    normal: {
                        lineStyle: {
                          width:1
                        }
                    },
                    emphasis : {
                        areaStyle: {color:'rgba(0,250,0,0.3)'}
                    }
                },
                data:[
                  {
                    value:da[i],
                    name:reg[i]
                  }
                ]
            })
        }
        return series;
    })()
        })
        myChart.hideLoading()
      }, 2000)
    }
}}
</script>

<style>
</style>