package googlejam8.p326;
import java.io.*;
import java.util.*;
import java.text.*;
import java.math.*;
import java.util.regex.*;

public class Solution {
	
    public static void main(String[] xaiAlpha000) {
        /* Enter your code here. Read input from STDIN. Print output to STDOUT. Your class should be named Solution. */
    Scanner xaiAlpha004=new Scanner(System.in);
   
    int xaiAlpha010=xaiAlpha004.nextInt();
    String xaiAlpha008[]=new String[xaiAlpha010];
    for(int xaiAlpha009=0;xaiAlpha009<xaiAlpha010;xaiAlpha009++){
    	StringBuilder xaiAlpha006=new StringBuilder();
    int xaiAlpha002=xaiAlpha004.nextInt();
    int[] xaiAlpha011=new int[xaiAlpha002];
    int xaiAlpha005=0;
    for(int xaiAlpha001=0;xaiAlpha001<xaiAlpha002;xaiAlpha001++){
    	xaiAlpha011[xaiAlpha001]=xaiAlpha004.nextInt();
    	xaiAlpha005+=xaiAlpha011[xaiAlpha001];
    }
    while(xaiAlpha005>0){
    	int xaiAlpha007=0,smax=0,tmax=0;
    	char xaiAlpha003='A',d='A';
    	for(int xaiAlpha001=0;xaiAlpha001<xaiAlpha002;xaiAlpha001++){
    		if(xaiAlpha011[xaiAlpha001]>=xaiAlpha011[xaiAlpha007]){
    			tmax=smax;
    			smax=xaiAlpha007;
    			xaiAlpha007=xaiAlpha001;
    		}
    	}
    		if(xaiAlpha011[xaiAlpha007]==xaiAlpha011[smax]&&xaiAlpha011[xaiAlpha007]==xaiAlpha011[tmax]&&smax!=tmax){
    			if(xaiAlpha011[xaiAlpha007]>0){xaiAlpha011[xaiAlpha007]-=1;
    			xaiAlpha003+=xaiAlpha007;
    			xaiAlpha006.append(xaiAlpha003);
    			xaiAlpha005-=1;
    			}
    		}
    		else if(xaiAlpha011[xaiAlpha007]-xaiAlpha011[smax]>1){
    			if(xaiAlpha011[xaiAlpha007]>0){xaiAlpha011[xaiAlpha007]-=1;
    			xaiAlpha003+=xaiAlpha007;
    			xaiAlpha006.append(xaiAlpha003);
    			xaiAlpha005-=1;
    			}
    			if(xaiAlpha011[xaiAlpha007]>0){xaiAlpha011[xaiAlpha007]-=1;
    			xaiAlpha006.append(xaiAlpha003);
    			xaiAlpha005-=1;
    			}
    		}
    		else{
    		if(xaiAlpha011[xaiAlpha007]>0){	xaiAlpha011[xaiAlpha007]-=1;
    			xaiAlpha003+=xaiAlpha007;
    			xaiAlpha006.append(xaiAlpha003);
    			xaiAlpha005-=1;}
    		if(xaiAlpha011[smax]>0){xaiAlpha011[smax]-=1;
    			d+=smax;
    			xaiAlpha006.append(d);
    			xaiAlpha005-=1;}
    		}
    		xaiAlpha006.append(" ");
    	}
    xaiAlpha008[xaiAlpha009]=xaiAlpha006.toString();
    }
    
    	
   
    for(int xaiAlpha009=0;xaiAlpha009<xaiAlpha010;xaiAlpha009++){
    	System.out.println("Case #"+(xaiAlpha009+1)+": "+xaiAlpha008[xaiAlpha009]);
    }
    } 
    }
