<template id="info1">
  <div id="info1" style="width:340px; height:500px;overflow:auto">
    <a>企业主体信息:</a>
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
    axios.get('https://api.qianzhan.com/OpenPlatformService/OrgCompany?token='+response.data.result.token+'&type=JSON&companyName='+key+'&areaCode=&page=1&pagesize=2').then(function (response) {
    var result = response.data.result[0]
    let tr = document.createElement('tr')
    tr.innerHTML = '<br><a>公司编号：' + result.companyCode + '</a>'
    let tr2 = document.createElement('tr')
    tr2.innerHTML = '<a>公司名称：' + result.companyName + '</a>'
    let tr3 = document.createElement('tr')
    tr3.innerHTML = '<a>注册代码：' + result.regNumber + '</a>'
    let tr4 = document.createElement('tr')
    tr4.innerHTML = '<a>所在地区：' + result.areaName + '</a>'
    let tr5 = document.createElement('tr')
    tr5.innerHTML = '<a>行业分类：' + result.companyType + '</a>'
    let tr6 = document.createElement('tr')
    tr6.innerHTML = '<a>注册时间：' + result.issueTime + '</a>'
    let tr7 = document.createElement('tr')
    tr7.innerHTML = '<a>注册地：' + result.regOrgName + '</a>'
    let tr8 = document.createElement('tr')
    tr8.innerHTML = '<a>经营范围：' + result.bussinessDes + '</a>'
    let tr9 = document.createElement('tr')
    tr9.innerHTML = '<a>经营状况：' + result.businessStatus + '</a>'
    let tr10 = document.createElement('tr')
    tr10.innerHTML = '<a>法人：' + result.faRen + '</a>'
    let tr11 = document.createElement('tr')
    tr11.innerHTML = '<a>注册资本（人民币）：' + result.regM + '</a>'
    let tr12 = document.createElement('tr')
    tr12.innerHTML = '<a>股权所有制：' + result.regType + '</a>'
    let tr13 = document.createElement('tr')
    tr13.innerHTML = '<a>地址：' + result.address + '</a>'

    document.getElementById('info1').appendChild(tr)
    document.getElementById('info1').appendChild(tr2) 
    document.getElementById('info1').appendChild(tr3)
    document.getElementById('info1').appendChild(tr4)
    document.getElementById('info1').appendChild(tr5)
    document.getElementById('info1').appendChild(tr6)
    document.getElementById('info1').appendChild(tr7)
    document.getElementById('info1').appendChild(tr8)
    document.getElementById('info1').appendChild(tr9)
    document.getElementById('info1').appendChild(tr10)
    document.getElementById('info1').appendChild(tr11)
    document.getElementById('info1').appendChild(tr12)
    document.getElementById('info1').appendChild(tr13)
    })
  .catch(function (response) {
    console.log(response)
  })})
    }
}}
</script>

<style>
</style>