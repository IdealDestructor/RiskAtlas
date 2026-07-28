<template id="category1">
  <div id="category1" class="box" style="width:400px; height:400px">
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
var dic=[{"个体":1},{"软件":1,"计算":1,"科技":1},{"超市":1,"销售":1,"商业":1,"商贸":1,"购物":1,"广场":1,"批发":1},{"水产":1,"羊肉":1,"牛肉":1,"面食":1,"火锅":1,"海鲜":1,"食品":1,"酒业":1,"美食":1,"糕点":1,"饮料":1,"饮品":1,"山泉":1,"乳业":1},{"果蔬":1,"水果":1,"蔬菜":1,"菜市":1},{"饭店":1,"酒店":1,"粮油":1,"酒庄":1,"小吃":1,"公寓":1,"餐厅":1,"餐馆":1},{"医院":1,"药业":1,"制药":1,"药店":1,"医药":1,"医疗":1},{"学校":1,"大学":1,"中学":1,"食堂":1},{"加油":1,"钢铁":1},{"肥料":1,"农业":1,"种业":1,"农药":1,"农机":1}]
		var str ='食品'
		for (var i = 0; i < key.length-1; i++) {
			var s = key.substring(i, i + 2);
      for (var k=0;k<9;k++){
			if (s in dic[k]) {
        str=s
			}}
}
        var keyreg=str
        var that = this
        var myChart = that.$echarts.init(document.getElementById('category1'))
        myChart.showLoading()
        var result1= []
        var obj = {}
        var obj1 = {}
        var reg=[]
        var reg1=[]
        var da=[]
        var dat=[]
        var data=[]

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
                reg1.push(result1[p].name)
              }
            }
            for (var q = 0; q < reg.length; q++) {
            var go=0
            var ba=0
            var si=0
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
            si =go-ba
            if(si<0){
                var ab=Math.abs(si)
                var abb={value : ab, itemStyle:{ normal:{color:'red'}}}
                data.push(abb)
            }
            da.push(go)
            dat.push(ba)
            if (si>=0)
            {data.push(si)}
            }
          }
        }
      })
      setTimeout(() => {
    myChart.setOption({
      
    title :{
        text : '本行业/地区舆情分布',
        subtext : '正负向比对'
    },
    toolbox: {
        orient : 'vertical',
        y:'center',
        show : true,
        feature : {
            mark : {show: true},
            dataView : {show: true, readOnly: false},
            magicType : {show: true, type: ['line', 'bar']},
            restore : {show: true},
            saveAsImage : {show: true}
        }
    },
    legend: {
        data:['正向', '负向'],
        selectedMode:false,
        x : 'right'
    },
    xAxis : [
        {
            type : 'category',
            data : reg
        }
    ],
    yAxis : [
        {
            type : 'value',
            min : 0,
            max : 15
        }
    ],
    series : [
        {
            name:'正向',
            type:'line',
            data: da
        },
        {
            name:'负向',
            type:'line',
            symbol:'none',
            itemStyle:{
                normal:{
                  lineStyle: {
                    width:1,
                    type:'dashed'
                  }
                }
            },
            data: dat
        },
        {
            name:'负向2',
            type:'bar',
            stack: '1',
            barWidth: 6,
            itemStyle:{
                normal:{
                    color:'rgba(0,0,0,0)'
                },
                emphasis:{
                    color:'rgba(0,0,0,0)'
                }
            },
            data: dat
        },
        {
            name:'变化',
            type:'bar',
            stack: '1',
            data:data
        }
    ]
    })
        myChart.hideLoading()
      }, 2000)
    }
}}
</script>

<style>
</style>