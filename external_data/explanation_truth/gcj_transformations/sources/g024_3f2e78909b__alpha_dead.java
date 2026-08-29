package googlejam2.p304;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.*;


public class Problem1 {
    public static void main(String[] xaiAlpha000) {
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

	try {
	    BufferedReader xaiAlpha006 = new BufferedReader(new FileReader("A-small-attempt0.in"));
		String xaiAlpha005 = null;
		List<String> xaiAlpha001 = new ArrayList<String>();
		while((xaiAlpha005 = xaiAlpha006.readLine()) != null) {
		    xaiAlpha001.add(xaiAlpha005);
		}
		xaiAlpha006.close();
		List<String> xaiAlpha011 = xaiAlpha001;
		List<String> xaiAlpha012 = new ArrayList<String>();
		int xaiAlpha003 = 0;
		int xaiAlpha018 = Integer.parseInt(xaiAlpha011.get(xaiAlpha003++));
		int xaiAlpha014 = 1000000;
		int[] xaiAlpha017 = new int[xaiAlpha014+1]; 
		Arrays.fill(xaiAlpha017, xaiAlpha014);
		xaiAlpha017[1] = 1;
		for(int xaiAlpha020=1;xaiAlpha020<xaiAlpha014;xaiAlpha020++) {
		    xaiAlpha017[xaiAlpha020+1] = Math.min(xaiAlpha017[xaiAlpha020]+1, xaiAlpha017[xaiAlpha020+1]);
			int xaiAlpha002 = xaiAlpha020;
			long xaiAlpha019 = 0;
			while (xaiAlpha002 != 0)
			{
			    xaiAlpha019 = xaiAlpha019*10 + xaiAlpha002 % 10;
			    xaiAlpha002 /= 10;
			}
		    long xaiAlpha007 = xaiAlpha019;
		    if(xaiAlpha007 > xaiAlpha014) {
			continue;
		    }
		    xaiAlpha017[(int)xaiAlpha007] = Math.min(xaiAlpha017[xaiAlpha020]+1, xaiAlpha017[(int)xaiAlpha007]);
		}
		for(int xaiAlpha022 = 0; xaiAlpha022 < xaiAlpha018; xaiAlpha022++) {
		    int xaiAlpha013 = Integer.parseInt(xaiAlpha011.get(xaiAlpha003++));
		    String xaiAlpha004 = "Case #" + (xaiAlpha022+1) + ": " +xaiAlpha017[xaiAlpha013];
		    System.out.println(xaiAlpha004);
		    xaiAlpha012.add(xaiAlpha004);
		}
		StringBuilder xaiAlpha010 = new StringBuilder("");
		if (xaiAlpha012 != null) {
		    int xaiAlpha020 = 0;
		    for (Object xaiAlpha008 : xaiAlpha012) {
			String xaiAlpha016 = xaiAlpha008.toString();
			if (xaiAlpha020 == 0) {
			    xaiAlpha010.append(xaiAlpha016);
			} else {
			    xaiAlpha010.append("\n");
			    xaiAlpha010.append(xaiAlpha016);
			}
			xaiAlpha020++;
		    }
		}
		String xaiAlpha021 = xaiAlpha010.toString();
		FileWriter xaiAlpha015 = new FileWriter("A-small-attempt0.in".replace(".in", ".out"));
		xaiAlpha015.write(xaiAlpha021);
		xaiAlpha015.close();
	}catch(Exception xaiAlpha009) {
	    xaiAlpha009.printStackTrace();
	}
    }


}
