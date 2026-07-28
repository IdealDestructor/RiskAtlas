package com.helloservlet.hello;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.sql.*;

import net.sf.json.JSONArray;
import net.sf.json.JSONObject;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class HelloWorldServlet extends HttpServlet {
	@Override 
	protected void doGet(HttpServletRequest request,HttpServletResponse response) throws ServletException,IOException{
		doPost(request, response);
	}@Override 
	protected void doPost(HttpServletRequest request,HttpServletResponse response) throws ServletException,IOException{
		//创建了一个bardao的对象，barDAO主要是对数据库的连接和对数据库的操作
        barDAO bardao=new barDAO();
        String keyword = request.getParameter("keyword");	
		//调用bardao的select_all()方法把从数据库中读取所有的数据返回的是一个ArrayList，ArrayList里面放的是一个barBean
        ArrayList<barBean> array = bardao.select_all(keyword);
        //设置返回时的编码格式
        response.setContentType("application/json; charset=utf-8");
        //调用JSONArray.fromObject方法把array中的对象转化为JSON格式的数组
        JSONArray json=JSONArray.fromObject(array);
        System.out.println(json.toString());
        //返回给前段页面
        PrintWriter out = response.getWriter();  
        out.println(json);  
        out.flush();  
        out.close();  
	         
	}
}
