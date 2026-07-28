<template id="info3">
  <div id="info3" style="width:280px; height:500px;overflow:auto">
  <a>司法风险：</a><p></p>
  <p id="tr666"><br><br><br><br><br><br><br><br><br><br><br>暂无该公司相关判决文书<br><br><br><br><br><br><br></p>
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
    axios.get('https://api.qianzhan.com/OpenPlatformService/JudgeQuery?token='+response.data.result.token+'&type=JSON&input='+key+'&page=1&pagesize=10').then(function (response) {
    var result = response.data.result
    for(var i=0;i<result.length;i++){
    let tr = document.getElementById('tr666')
    tr.innerHTML = '<br><a>判决编号：' + result[i].judgeId + '</a>'
    let tr2 = document.createElement('tr')
    tr2.innerHTML = '<a>机构代码：' + result[i].companyCodePlaintiff + '</a>'
    let tr3 = document.createElement('tr')
    tr3.innerHTML = '<a>公司编码：' + result[i].companyCodeDefendant + '</a>'
    let tr4 = document.createElement('tr')
    tr4.innerHTML = '<a>判决名称：' + result[i].title + '</a>'
    let tr5 = document.createElement('tr')
    tr5.innerHTML = '<a>法院：' + result[i].ch + '</a>'
    let tr6 = document.createElement('tr')
    tr6.innerHTML = '<a>编号：' + result[i].num + '</a>'
    let tr7 = document.createElement('tr')
    tr7.innerHTML = '<a>判决结果：' + result[i].content + '</a>'
    let tr8 = document.createElement('tr')
    tr8.innerHTML = '<a>裁定日期：' + result[i].date + '</a>'
    let tr9 = document.createElement('tr')
    
    document.getElementById('info3').appendChild(tr)
    document.getElementById('info3').appendChild(tr2) 
    document.getElementById('info3').appendChild(tr3)
    document.getElementById('info3').appendChild(tr4)
    document.getElementById('info3').appendChild(tr5)
    document.getElementById('info3').appendChild(tr6)
    document.getElementById('info3').appendChild(tr7)
    document.getElementById('info3').appendChild(tr8)
    document.getElementById('info3').appendChild(tr9)
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