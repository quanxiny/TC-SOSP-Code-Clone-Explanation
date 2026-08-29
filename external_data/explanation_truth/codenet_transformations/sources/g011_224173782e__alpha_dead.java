import java.io.*;
import java.math.*;
import java.util.*;
public class Main { 

	public static void main(String[] xaiAlpha000) {
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }
 
		Scanner xaiAlpha006 = new Scanner(System.in); 
		String xaiAlpha004 = xaiAlpha006.next();
		int xaiAlpha003 = xaiAlpha004.length();
		int xaiAlpha002=0;
		boolean xaiAlpha001=false;
		while (xaiAlpha002<xaiAlpha003) {
			if (xaiAlpha002+5<=xaiAlpha003) {
				String xaiAlpha005 = xaiAlpha004.substring(xaiAlpha002,xaiAlpha002+5);
				if (xaiAlpha005.equals("dream")) {
					xaiAlpha002+=5;
					if (xaiAlpha002+2<=xaiAlpha003) {
						if (xaiAlpha004.substring(xaiAlpha002,xaiAlpha002+2).equals("er")) {
							xaiAlpha002+=2;
						}
					}
					if (xaiAlpha002+1<=xaiAlpha003) {
						if (xaiAlpha004.substring(xaiAlpha002,xaiAlpha002+1).equals("a")) {
							xaiAlpha002-=2;
							//Reset due to erase word being after dream 
							//(not dreamer)
						}
					}
				}else if (xaiAlpha005.equals("erase")) {
					xaiAlpha002+=5;
					if (xaiAlpha002<xaiAlpha003) {
						if (xaiAlpha004.charAt(xaiAlpha002)=='r') xaiAlpha002++;
					}
				}else {
					xaiAlpha001=true;
				}
			}else {
				if (xaiAlpha003-xaiAlpha002>1) {
					xaiAlpha001=true;
					break;
				} 
			}
			if (xaiAlpha001) break;
		}
		System.out.println(xaiAlpha001?"NO":"YES");
	}	
}