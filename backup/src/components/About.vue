<template>
  <div id="About">
    <br/>
    <a> 基于机构实体的智能摘要和风险等级识别可视化系统 </a>
    <p> Visualization System Of Intelligent Abstract And Risk Grading Based On Institutional Entities </p>
    <p>     通过机器学习等数据分析方法，可以挖掘蕴含在数据资源中的价值，以学科交叉的形式推动社会治理和产业结构升级。在金融风控领域，为了满足商业银行、征信公司、金融信贷机构对高精度舆情大数据的迫切需求，通过采集由司法、财经、科技、质量监督类权威媒体发布的新闻并进行数据清洗，采用高效的算法模型提取出机构实体并生成基于该实体的摘要、关键词和风险等级的智能文摘。在前人已有的工作基础上，综合应用HTML、CSS、JavaScript等前端技术，使用Vue、Echarts等工具，并采用Ajax方法和Java语言实现与数据库的动态交互，以多种方式实现被检索机构的风险评估结果和征信排名可视化，以满足众多银行、征信、互金机构客户的实际需要，延伸这一解决方案的应用价值与现实意义。</p>
    <a> 当前版本： {{ url }} </a>
  </div>
</template>

<script>
export default {
  data () {
    return {
      url: '9.8.5'
    }
  }
}
</script>

<style>
</style>
