<template id="info2">
  <div id="info2" style="width:280px; height:500px;overflow:auto">
    <a>失信与被执行情况：</a><p></p>
    <p id="tr666"><br><br><br><br><br><br><br><br><br><br><br>本企业暂无失信记录<br><br><br><br><br><br><br></p>
  </div>
</template>

<script>
import jQuery from 'jquery'
import axios from 'axios'
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
    axios.get('https://api.qianzhan.com/OpenPlatformService/GetToken?type=JSON&appkey=a13b3ea692775f40&seckey=1403a899d26bbdb4').then(response => {
    axios.get('https://api.qianzhan.com/OpenPlatformService/DishonestQuery?token='+response.data.result.token+'&type=JSON&input='+key+'&areaCode=&page=1&pagesize=2').then(function (response) {
    var result = response.data.result
    for(var i=0;i<result.length;i++){
    let tr = document.getElementById('tr666')
    tr.innerHTML = '<br><a>国家失信查询平台记录码：' + result[i].dishonestId + '</a>'
    let tr2 = document.createElement('tr')
    tr2.innerHTML = '<a>被执行人：' + result[i].dishonestName + '</a>'
    let tr3 = document.createElement('tr')
    tr3.innerHTML = '<a>代号：' + result[i].caseCode + '</a>'
    let tr4 = document.createElement('tr')
    tr4.innerHTML = '<a>执行记录：' + result[i].cardNum + '</a>'
    let tr5 = document.createElement('tr')
    tr5.innerHTML = '<a>法人：' + result[i].businessEntity + '</a>'
    let tr6 = document.createElement('tr')
    tr6.innerHTML = '<a>判决法院：' + result[i].courtName + '</a>'
    let tr7 = document.createElement('tr')
    tr7.innerHTML = '<a>所在地区：' + result[i].areaName + '</a>'
    let tr8 = document.createElement('tr')
    tr8.innerHTML = '<a>判决编号：' + result[i].gistId + '</a>'
    let tr9 = document.createElement('tr')
    tr9.innerHTML = '<a>执行法院：' + result[i].gistUnit + '</a>'
    let tr10 = document.createElement('tr')
    tr10.innerHTML = '<a>日期：' + result[i].legalDuty + '</a>'
    let tr11 = document.createElement('tr')
    tr11.innerHTML = '<a>执行日期：' + result[i].publishDate + '</a>'
    let tr12 = document.createElement('tr')
    tr12.innerHTML = '<a>失信情况：' + result[i].performance + '</a>'
    let tr13 = document.createElement('tr')
    tr13.innerHTML = '<a>被执行原因：' + result[i].disruptTypeName + '</a>'

    document.getElementById('info2').appendChild(tr)
    document.getElementById('info2').appendChild(tr2) 
    document.getElementById('info2').appendChild(tr3)
    document.getElementById('info2').appendChild(tr4)
    document.getElementById('info2').appendChild(tr5)
    document.getElementById('info2').appendChild(tr6)
    document.getElementById('info2').appendChild(tr7)
    document.getElementById('info2').appendChild(tr8)
    document.getElementById('info2').appendChild(tr9)
    document.getElementById('info2').appendChild(tr10)
    document.getElementById('info2').appendChild(tr11)
    document.getElementById('info2').appendChild(tr12)
    document.getElementById('info2').appendChild(tr13)
    }}
    )
  .catch(function (response) {
    console.log(response)
  })})
    }
}}
</script>

<style>
</style>