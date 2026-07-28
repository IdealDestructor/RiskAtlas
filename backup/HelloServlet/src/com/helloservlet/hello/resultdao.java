package com.helloservlet.hello;

import java.sql.*;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;

import javax.naming.InitialContext;
import javax.naming.NamingException;
import javax.sql.DataSource;

import java.sql.Connection;  
import java.sql.DriverManager;  
import java.sql.PreparedStatement;  

  
  
public class resultdao {  
    // 连接驱动  a
    private static final String DRIVER = "com.microsoft.jdbc.sqlserver.SQLServerDriver";  
    // 连接路径  
    private static final String URL = "jdbc:sqlserver://localhost:1433;databaseName=test";  
    // 用户名  
    private static final String USERNAME = "sa";  
    // 密码  
    private static final String PASSWORD = "wdq.13293807356"; 
    // 动态SQL
    private static final String SELECT_ALL = "SELECT top 220 [dbo].[p].name,[dbo].[p].eventLevel,distinct [dbo].[y].srcUrl,distinct [dbo].[y].title,distinct [dbo].[y].postTime,distinct [dbo].[d].digest FROM [dbo].[p],[dbo].[y],[dbo].[d] WHERE [dbo].[p].name = ? and [dbo].[p].newsId = [dbo].[y].newsId and [dbo].[d].newsId = [dbo].[y].newsId";
    //静态代码块
    static {  
        try {  
            // 加载驱动  
            Class.forName(DRIVER);  
        } catch (ClassNotFoundException e) {  
            e.printStackTrace();  
        }  
    }  
  
    /* 
     * 获取数据库连接 
     */   
    public ArrayList<barBean> select_all(String keyword)
    {
        try{
        	Connection conn=DriverManager.getConnection(URL, USERNAME, PASSWORD);  
        	PreparedStatement pstmt = conn.prepareStatement(SELECT_ALL);
        	pstmt.setString(1, keyword);  
        	ResultSet rst = pstmt.executeQuery(); 
            ArrayList<barBean> array = new ArrayList<barBean>();
            while(rst.next())
            {
                barBean bar = new barBean();
                bar.setname(rst.getString("name"));
                bar.seteventLevel(rst.getString("eventLevel"));
                bar.seturl(rst.getString("srcUrl"));
                bar.settitle(rst.getString("title"));
                bar.settime(rst.getString("postTime"));
                bar.setdigest(rst.getString("digest"));
               // bar.setindex(rst.getString("index"));
                array.add(bar);
            }
            pstmt.close();
            rst.close();
            conn.close();
            return array;
        }catch(Exception e){
            System.out.println("Error occured at barDAO->select_all()");
            return new ArrayList<barBean>();
        }
    }
    /* 
     * 关闭数据库连接，注意关闭的顺序 
     */  
    public void close(ResultSet rs, PreparedStatement ps, Connection conn) {  
        if(rs!=null){  
            try{  
                rs.close();  
                rs=null;  
            }catch(SQLException e){  
                e.printStackTrace();  
            }  
        }  
        if(ps!=null){  
            try{  
                ps.close();  
                ps=null;  
            }catch(SQLException e){  
                e.printStackTrace();  
            }  
        }  
        if(conn!=null){  
            try{  
                conn.close();  
                conn=null;  
            }catch(SQLException e){  
                e.printStackTrace();  
            }  
        }  
    }  
}  