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

  
  
public class barDAO {  
    // ��������  a
    private static final String DRIVER = "com.microsoft.jdbc.sqlserver.SQLServerDriver";  
    // ����·��  
    private static final String URL = "jdbc:sqlserver://localhost:3306;databaseName=yutu";
    // �û���  
    private static final String USERNAME = "yutu";
    // ����  
    private static final String PASSWORD = "";
    // ��̬SQL
    private static final String SELECT_ALL = "SELECT top 300 [dbo].[p].name,[dbo].[p].eventLevel,distinct [dbo].[y].srcUrl,distinct [dbo].[y].title,distinct [dbo].[y].postTime,distinct [dbo].[d].digest FROM [dbo].[p],[dbo].[y],[dbo].[d] WHERE [dbo].[p].name =? and [dbo].[p].newsId = [dbo].[y].newsId and [dbo].[d].newsId = [dbo].[y].newsId";
    //��̬�����
    static {  
        try {  
            // ��������  
            Class.forName(DRIVER);  
        } catch (ClassNotFoundException e) {  
            e.printStackTrace();  
        }  
    }  
  
    /* 
     * ��ȡ���ݿ����� 
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
     * �ر����ݿ����ӣ�ע��رյ�˳�� 
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