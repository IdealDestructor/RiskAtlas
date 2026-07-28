<template id="view3">
  <div id="echartContainer2" style="height:400px;width:400px">
  </div>
</template>
<script>
import jQuery from 'jquery'
import { getAddr } from '../addresses'
export default {
  name: 'bar-chart',
  data () {
    return {
      tooltip: {},
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'value'
      },
      yAxis: {
        type: 'category',
        axisTick: {show: false},
        data: ['2016/4', '2016/8', '2016/12', '2017/4', '2017/8', '2017/12']
      },
      series: [{
        name: '等级',
        type: 'bar',
        label: {
          noraml: {
            show: true,
            position: 'inside'
          }
        },
        data: [1, 2, 3]
      }]
    }
  },
  computed: {
    cha () {
      return this.$store.state.cha
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
      var myChart = that.$echarts.init(document.getElementById('echartContainer2'), 'infographic')
      myChart.showLoading()
      var change = [0, 0, 0, 0, 0, 0]
      var cha = []
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
              if (result1[i].time < 1460049440000) {
                if (result1[i].eventLevel === '正向') {
                  change[0]++
                } else if(result1[i].eventLevel === '负向'){
                  change[0]--
                }
              } else {
                if (result1[i].time < 1470049440000) {
                  if (result1[i].eventLevel === '正向') {
                    change[1]++
                  } else if(result1[i].eventLevel === '负向'){
                    change[1]--
                  }
                } else {
                  if (result1[i].time < 1480049440000) {
                    if (result1[i].eventLevel === '正向') {
                      change[2]++
                    } else if(result1[i].eventLevel === '负向'){
                      change[2]--
                    }
                  } else {
                    if (result1[i].time < 1490049440000) {
                      if (result1[i].eventLevel === '正向') {
                        change[3]++
                      } else if(result1[i].eventLevel === '负向'){
                        change[3]--
                      }
                    } else {
                      if (result1[i].time < 1500049440000) {
                        if (result1[i].eventLevel === '正向') {
                          change[4]++
                        } else if(result1[i].eventLevel === '负向'){
                          change[4]--
                        }
                      } else {
                        if (result1[i].eventLevel === '正向') {
                          change[5]++
                        } else if(result1[i].eventLevel === '负向'){
                          change[5]--
                        }
                      }
                    }
                  }
                }
              }
            }
            cha = change
          }
        }
      })
      setTimeout(() => {
        myChart.setOption({
          title: {
            x: 'center',
            text: '舆情趋势'
          },
          tooltip: {},
          grid: {
            left: '3%',
            right: '4%',
            containLabel: true
          },
          xAxis: {
            type: 'value'
          },
          yAxis: {
            type: 'category',
            axisTick: {show: false},
            data: ['2016年初', '2016年中', '2016年末', '2017年初', '2017年中', '2017年末']
          },
          series: [{
            name: '等级',
            type: 'line',
            label: {
              noraml: {
                show: true,
                position: 'inside'
              }
            },
            data: cha
          }]
        })
        myChart.hideLoading()
      }, 2000)
    }
  }
}
</script>

<style>
</style>