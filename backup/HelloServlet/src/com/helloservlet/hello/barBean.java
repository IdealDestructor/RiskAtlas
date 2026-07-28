package com.helloservlet.hello;

import java.io.Serializable;
import java.sql.Date;

public class barBean {
    private String name;
    private String eventLevel;
    private String srcUrl;
    private String title;
    private String postTime;
    private String digest;
    //private String index;
    public String getname() {
        return name;
    }
    public void setname(String name) {
        this.name = name;
    }
    public String geteventLevel() {
        return eventLevel;
    }
    public void seteventLevel(String eventLevel) {
        this.eventLevel = eventLevel;
    }
    public String geturl() {
        return srcUrl;
    }
	public void seturl(String srcUrl) {
		this.srcUrl = srcUrl;	
	}
	public String gettitle() {
        return title;
    }
	public void settitle(String title) {
		this.title = title;
	}
	public String gettime() {
        return postTime;
    }
	public void settime(String postTime) {
		this.postTime = postTime;	
	}
	public String getdigest() {
        return digest;
    }
	public void setdigest(String digest) {
		this.digest = digest;	
	}
	//public String getindex() {
      //  return index;
   // }
	//public void setindex(String index) {
	//	this.index = index;	
	//}
}
    