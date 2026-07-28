<template>
  <div id="view1">
  <!--创建一个echarts的容器-->
    <div id="pieContainer" style="height:400px;width:400px"></div>
  </div>
</template>

<script>
import jQuery from 'jquery'
import { getAddr } from '../addresses';
export default {
  name: '',
  data () {
    return {
    }
  },
  computed: {
    get () {
      return this.$store.state.get
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
      var myChart = that.$echarts.init(document.getElementById('pieContainer'))
      myChart.showLoading()
      var getoptiondata = []
      var get = []
      var wnum = 0
      var bnum = 0
      var fnum = 0
      var result1 = []
      var obj = {}
      var key = this.$store.state.keyword
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
              if (result1[i].eventLevel === '正向') {
                wnum++
              } else {
                if (result1[i].eventLevel === '中性') {
                  bnum++
                } else {
                  fnum++
                }
              }
            }
            getoptiondata.push({value: wnum, name: '正向'})
            getoptiondata.push({value: bnum, name: '中性'})
            getoptiondata.push({value: fnum, name: '负向'})
            get = getoptiondata
          }
        }
      })
      setTimeout(() => {
        myChart.setOption({
         title: {
            x: 'center',
            text: '情感倾向分布'
          },
         itemStyle: {
        normal: {
            shadowBlur: 0, // 阴影的大小
            shadowOffsetX: 0,// 阴影水平方向上的偏移
            shadowOffsetY: 0,
            shadowColor: 'rgba(0, 0, 0, 0)'
        }
    },
    backgroundColor: '#FFFFFF', //设置图标的背景色
    label: {
        normal: {
            fontStyle: 'italic' //文字字体的风格
        }
    },
    labelLine: {
        normal: {
            lineStyle: {
                color: 'rgba(255, 255, 255, 0.3)' //设置标签的视觉引导线
            }
        }
    },
    series:[
        {
            name: '舆情分布', //系列名称, 用于toolitp的显示
            type: 'pie', //图形的类型
            radius: '130', 
            data: get,
            itemStyle: {  //设置每个item的颜色
                normal: {
                    color: function(params) { //params是一个对象, 传入的是seriesIndex, dataIndex, data, value 等各个参数。
                        var colorList = [
                        '#B5C334','#FCCE10','#27727B',
                        '#FE8463','#9BCA63','#FAD860','#F3A43B','#60C0DD',
                        '#D7504B','#C6E579','#F4E001','#F0805A','#26C0C0'
                        ];
                        return colorList[params.dataIndex]
                    },
                    shadowBlur: 100,
                    shadowColor: 'rgba(0, 0, 0, 0)'
                }
            }
        }]})
        myChart.hideLoading()
      }, 2000)
    }
  }
}
</script>
        
<style scoped>  
</style>

