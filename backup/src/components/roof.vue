<template id="roof">
  <div>
    <h1>Risk Grading System</h1>
    <div class="div1"> 
      <table margin="0 auto"> 
        <tr>
          <td class="td1">""  ""   "</td> 
          <td  width="322px">
            <div>
              <input type="text" placeholder="请输入公司或机构名称" v-model="msg">
            </div>
          </td>
          <td width="100px">
            <div>
              <button @click="showChildComponentData">评估</button>
            </div>
          </td> 
        </tr>
      </table>
    </div>
    <div id="list1" v-for="item of select">
      <p class="selectionItem" @click="selectName(item)">{{item}}</p>
    </div>

    <P> 
    <router-link to="/search2">按地区/行业评估</router-link></P>
    <router-link to="/About">About</router-link>
    <img src="../assets/back2.jpg" width="100%" height="100%"> 
  </div>
</template>

<script type="text/javascript">
import jQuery from "jquery";
import { getAddr } from "../addresses";

var getname = [];
export default {
  data() {
    return {
      isshow: true,
      msg: "",
      films: [],
      select: [],
      number: "19982"
    };
  },
  methods: {
    showChildComponentData: function() {
      this.$store.state.keyword = this.msg;
      this.$router.push({ path: "/Result" });
    },
    selectName(item) {
      console.log(item)
      this.msg = item
    }
  },
  watch: {
    msg: function(val, oldVal) {
      if (val.length === 0) {
        this.isshow = false;
      } else {
        var key = this.msg;
        jQuery.ajax({
          type: "post",
          async: false,
          url: getAddr("/servlet/helloWorld"),
          data: { keyword: key },
          dataType: "json",
          success: result => {
            getname = result.map(v => v.name);
            // document.getElementById("word").innerHTML = "";
            var res = [];
            var json = {};
            for (var i = 0; i < getname.length; i++) {
              if (!json[getname[i]]) {
                res.push(getname[i]);
                json[getname[i]] = 1;
              }
              this.select = res;
            }
            console.log(result, getname, this.select);
          },
          error: function() {
            console.log("Wrong");
          }
        });
        this.isshow = true;
      }
    }
  }
};1
</script>



<style scoped>
ul {
  border: none;
}
.div1 {
  margin: 0 auto;
  width: 500px;
}
li {
  height: 40px;
  line-height: 60px;
  border-bottom: 1px solid #ddd;
}
input {
  text-align: center;
  font-size: 1.4em;
  height: 2.3em;
  border-radius: 8px;
  border: 1px solid #c8cccf;
  color: #6a6f77;
  -moz-appearance: none;
  display: block;
  outline: 0;
  width: 100%;
}
.td1 {
  visibility: hidden;
}
button {
  background-color: #4caf50; /* Green */
  border: none;
  color: white;
  padding: 15px 32px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  margin: 16px 2px;
  cursor: pointer;
  -webkit-transition-duration: 0.4s; /* Safari */
  transition-duration: 0.4s;
  border-radius: 8px;
}
button:hover {
  box-shadow: 0 12px 16px 0 rgba(0, 0, 0, 0.24),
    0 17px 50px 0 rgba(0, 0, 0, 0.19);
}
.tbl {
  border: 1px solid lightgray;
}
list1{
width: 324px;
margin-left: 17.1%;
list-style: none;

}
.selectionItem {
  font-weight: lighter;
  font-size: 18px;
  width: 324px;
  cursor: pointer;
  border: 0.02px solid lightgray;
  margin-top: 0rem;
  margin-bottom: 0rem;
  margin-left:33.8%;
}
.selectionItem:hover {
  color: orange;
}
.selectionItem:last {
  margin-bottom: 0;
}
</style>

