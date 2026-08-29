package googlejam1.p099;

import java.io.*;
import java.util.*;

public class A {
	Scanner xaiAlpha012;
	PrintWriter xaiAlpha002;
	int xaiAlpha007;
	int[] xaiAlpha006;
	
	public static void main(String[] xaiAlpha001) throws Exception{
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

		String xaiAlpha005 = xaiAlpha001.length>0?xaiAlpha001[0]:"A-large (1)";

		try {
			A xaiAlpha004 = new A();
			xaiAlpha004.xaiAlpha012 = new Scanner(new FileReader(xaiAlpha005 + ".in"));
			xaiAlpha004.xaiAlpha002 = new PrintWriter(new FileWriter(xaiAlpha005 + ".out"));
			int xaiAlpha013 = xaiAlpha004.xaiAlpha012.nextInt();
			for(int xaiAlpha009=1; xaiAlpha009<=xaiAlpha013; xaiAlpha009++) {
				Scanner xaiAlpha012 = xaiAlpha004.xaiAlpha012;
				xaiAlpha004.xaiAlpha007 = xaiAlpha012.nextInt();
				xaiAlpha004.xaiAlpha006 = new int[xaiAlpha004.xaiAlpha007];
				for(int xaiAlpha011=0; xaiAlpha011<xaiAlpha004.xaiAlpha007; xaiAlpha011++)
					xaiAlpha004.xaiAlpha006[xaiAlpha011] = xaiAlpha012.nextInt();
				xaiAlpha004.xaiAlpha002.print("Case #" + xaiAlpha009 + ": ");
				System.out.print("Case #" + xaiAlpha009 + ": ");
				int xaiAlpha010 = 0,ans2 = 0;
				int xaiAlpha008 = 0;
				for(int xaiAlpha011=1; xaiAlpha011<xaiAlpha004.xaiAlpha007; xaiAlpha011++) {
					xaiAlpha010 += Math.max(xaiAlpha004.xaiAlpha006[xaiAlpha011-1]-xaiAlpha004.xaiAlpha006[xaiAlpha011], 0);
					xaiAlpha008 = Math.max(xaiAlpha004.xaiAlpha006[xaiAlpha011-1]-xaiAlpha004.xaiAlpha006[xaiAlpha011], xaiAlpha008);
				}
				
				for(int xaiAlpha011=1; xaiAlpha011<xaiAlpha004.xaiAlpha007; xaiAlpha011++) {
					ans2 += Math.min(xaiAlpha004.xaiAlpha006[xaiAlpha011-1], xaiAlpha008);
				}
				Object xaiAlpha000 = xaiAlpha010 + " " + ans2;
				
				xaiAlpha004.xaiAlpha002.println(xaiAlpha000);
				System.out.println(xaiAlpha000);
			}
			System.out.println("Finished.");
			xaiAlpha004.xaiAlpha012.close();
			xaiAlpha004.xaiAlpha002.close();
		} catch(Exception xaiAlpha003) {
			System.err.println(xaiAlpha003);
		}
	}
	
}
