package googlejam3.p340;


import java.io.File;
import java.io.IOException;
import java.io.PrintStream;
import java.util.Scanner;

public class R20151C_A {
	
	private int xaiAlpha014;
	
	public static void main(String[] xaiAlpha002) {
		R20151C_A xaiAlpha005 = new R20151C_A();
		File xaiAlpha000 = new File(xaiAlpha005.getClass().getSimpleName() + "_cases");
		File xaiAlpha012 = new File(xaiAlpha005.getClass().getSimpleName() + "_cases" + "/in");
		File xaiAlpha003 = new File(xaiAlpha005.getClass().getSimpleName() + "_cases" + "/out");
		
		if (!xaiAlpha000.isDirectory()) {
			xaiAlpha000.mkdir();
		}
		if (!xaiAlpha003.isDirectory()) {
			xaiAlpha003.mkdir();
		}
		if (!xaiAlpha012.isDirectory()) {
			xaiAlpha012.mkdir();
		}
		
		for (String xaiAlpha007 : xaiAlpha012.list()) {
			String xaiAlpha015 = xaiAlpha007.replace(".in", "");
			String xaiAlpha016 = xaiAlpha015 + ".out";
			
			
			PrintStream xaiAlpha009 = null;
			Scanner xaiAlpha001 = null;
			try {
				File xaiAlpha018 = new File(xaiAlpha005.getClass().getSimpleName() + "_cases" + "/in" + "/" + xaiAlpha007);
				File xaiAlpha006 = new File(xaiAlpha005.getClass().getSimpleName() + "_cases" + "/out" + "/" + xaiAlpha016);
				
				xaiAlpha009 = new PrintStream(xaiAlpha006);
				xaiAlpha001 = new Scanner(xaiAlpha018);
				
				xaiAlpha005.xaiAlpha014 = xaiAlpha001.nextInt();
				for (int xaiAlpha013 = 0; xaiAlpha013 < xaiAlpha005.xaiAlpha014; xaiAlpha013++) {
					xaiAlpha009.print("Case #" + (xaiAlpha013+1) + ": ");
					xaiAlpha005.xaiAlpha011 = xaiAlpha001.nextInt();
					xaiAlpha005.xaiAlpha010 = xaiAlpha001.nextInt();
					xaiAlpha005.xaiAlpha017 = xaiAlpha001.nextInt();
					xaiAlpha005.xaiAlpha008 = (xaiAlpha005.xaiAlpha010 / xaiAlpha005.xaiAlpha017) * (xaiAlpha005.xaiAlpha011 - 1);
					xaiAlpha005.xaiAlpha008 += Math.max(((xaiAlpha005.xaiAlpha010 - 1) / xaiAlpha005.xaiAlpha017) - 1, 0);
					xaiAlpha005.xaiAlpha008 += xaiAlpha005.xaiAlpha017 + (xaiAlpha005.xaiAlpha017 == xaiAlpha005.xaiAlpha010? 0 : 1);
					xaiAlpha009.println(xaiAlpha005.xaiAlpha008);
				}
			} catch (IOException xaiAlpha004) {
				xaiAlpha004.printStackTrace();
			} finally {
				if (xaiAlpha001 != null) {
					xaiAlpha001.close();
				}
				
				if (xaiAlpha009 != null) {
					xaiAlpha009.close();
				}
			}
				
			
		}
	}
	
	private int xaiAlpha011;
	
	private int xaiAlpha010;
	
	private int xaiAlpha017;
	
	private int xaiAlpha008;


}
