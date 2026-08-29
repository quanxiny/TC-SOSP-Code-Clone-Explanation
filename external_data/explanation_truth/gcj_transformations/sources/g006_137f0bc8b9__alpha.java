package googlejam8.p675;
import java.io.*;
import java.util.*;

public class JamProblems {

    public static void main(String[] xaiAlpha000) throws IOException {

        JamProblems xaiAlpha005 = new JamProblems();
		Scanner xaiAlpha010 = null;
			PrintWriter xaiAlpha003 = null;
			try {
				xaiAlpha010 = new Scanner(new File("A-large.in"));
				xaiAlpha003 = new PrintWriter(new File("output.out"));
			} catch (FileNotFoundException xaiAlpha004) {
				xaiAlpha004.printStackTrace();
			}
		    		
		    int xaiAlpha008 = xaiAlpha010.nextInt();
		    for (int xaiAlpha001 = 1; xaiAlpha001 <= xaiAlpha008; xaiAlpha001++) { 	  
		    	xaiAlpha003.print("Case #" + xaiAlpha001 + ": ");
			    int xaiAlpha002 = xaiAlpha010.nextInt();
			    int[] xaiAlpha006 = new int[xaiAlpha002];
			    Map<Integer, Integer> xaiAlpha012 = new HashMap<Integer, Integer>();
			    String xaiAlpha013 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
			    int xaiAlpha011 = 0;
			    for(int xaiAlpha009 = 0; xaiAlpha009 < xaiAlpha002; xaiAlpha009++) {
			    	xaiAlpha006[xaiAlpha009] = xaiAlpha010.nextInt();
			    	xaiAlpha012.put(xaiAlpha009, xaiAlpha006[xaiAlpha009]);
			    	xaiAlpha011 += xaiAlpha006[xaiAlpha009];
			    }
			    //pw.print(partNames.charAt(0));
			    
			    while(true) {
			    	int xaiAlpha014 = 0, sMaxInd = 0, maxEm = 0;
			    	for(int xaiAlpha007 = 0; xaiAlpha007 < xaiAlpha002; xaiAlpha007++) {
			    		if(xaiAlpha006[xaiAlpha007] > maxEm) {
			    			maxEm = xaiAlpha006[xaiAlpha007];
			    			xaiAlpha014 = xaiAlpha007;
			    		}
			    	}
			    	if(xaiAlpha011 == 3) {
			    		xaiAlpha003.print(xaiAlpha013.charAt(xaiAlpha014) + " ");
			    		xaiAlpha006[xaiAlpha014]--;
			    	} else {
			    		maxEm = 0;
			    		for(int xaiAlpha007 = 0; xaiAlpha007 < xaiAlpha002; xaiAlpha007++) {
		    	    		if(xaiAlpha007 != xaiAlpha014 && xaiAlpha006[xaiAlpha007] > maxEm) {
		    	    			maxEm = xaiAlpha006[xaiAlpha007];
		    	    			sMaxInd = xaiAlpha007;
		    	    		}
		    	    	}
			    		xaiAlpha003.print(xaiAlpha013.charAt(xaiAlpha014) + "" + xaiAlpha013.charAt(sMaxInd) + " ");
			    		xaiAlpha006[xaiAlpha014]--;
			    		xaiAlpha006[sMaxInd]--;
			    	}	
			    	xaiAlpha011 = 0;
			    	for(int xaiAlpha009 = 0; xaiAlpha009 < xaiAlpha002; xaiAlpha009++) {
			    		xaiAlpha011 += xaiAlpha006[xaiAlpha009];
			    	}
			    	if(xaiAlpha011 == 0) break;
			    }
			    xaiAlpha003.println();
		  } 
		
		  xaiAlpha003.close();
    }
    
}