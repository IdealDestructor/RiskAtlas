<template id="API1">
  <div id="API1" class="box" style="width:400px; height:400px">
  </div>
</template>

<script>
import jQuery from 'jquery'
import axios from 'axios'
  import data222 from '../api/webkit-dep.json'
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
        var myChart = that.$echarts.init(document.getElementById('API1'))
var data=data222
myChart.setOption({
    title : {
        text: 'webkit内核依赖',
        subtext: '数据来自网络',
        x:'right',
        y:'bottom'
    },
    tooltip : {
        trigger: 'item',
        formatter : "{b}"
    },
    toolbox: {
        show : true,
        feature : {
            restore : {show: true},
            magicType: {
                show: true,
                type: ['force', 'chord'],
                option: {
                    chord: {
                        minRadius : 2,
                        maxRadius : 10,
                        ribbonType: false,
                        itemStyle: {
                            normal: {
                                label: {
                                    show: true,
                                    rotate: true
                                },
                                chordStyle: {
                                    opacity: 0.2
                                }
                            }
                        }
                    },
                    force: {
                        minRadius : 5,
                        maxRadius : 8,
                        itemStyle : {
                            normal : {
                                label: {
                                    show: false
                                },
                                linkStyle : {
                                    opacity : 0.5
                                }
                            }
                        }
                    }
                }
            },
            saveAsImage : {show: true}
        }
    },
    legend : {
        data : ['HTMLElement', 'WebGL', 'SVG', 'CSS', 'Other'],
        orient : 'vertical',
        x : 'left'
    },
    noDataEffect: 'none',
    series :[{
        //FIXME No data
        type: 'force',
    }],
});
 
        option.series[0] = {
            type: 'force',
            name: 'webkit-dep',
            itemStyle: {
                normal : {
                    linkStyle : {
                        opacity : 0.5
                    }
                }
            },
            categories: data.categories,
            nodes: data.nodes,
            links: data.links,
            minRadius: 5,
            maxRadius: 8,
            gravity: 1.1,
            scaling: 1.1,
            steps: 20,
            large: true,
            useWorker: true,
            coolDown: 0.995,
            ribbonType: false}

        myChart.setOption(option);
        myChart.hideLoading();
    
}}}
</script>
<style>
</style>  