package googlejam1.p403;


import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.util.StringTokenizer;

public class Welcome {
	public static void main(String[] xaiAlpha001) throws Exception {
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

		FileInputStream xaiAlpha005 = null;
		BufferedReader xaiAlpha006 = null;
		BufferedWriter xaiAlpha012 = new BufferedWriter(new OutputStreamWriter(new FileOutputStream("/home/luong/Downloads/"+xaiAlpha001[0]+".out", true)));

		String xaiAlpha000;
		xaiAlpha005 = new FileInputStream("/home/luong/Downloads/"+xaiAlpha001[0]+".in");
		xaiAlpha006 = new BufferedReader(new InputStreamReader(xaiAlpha005));
		xaiAlpha000 = xaiAlpha006.readLine();
		int xaiAlpha014 = Integer.parseInt(xaiAlpha000);
		for (int xaiAlpha013 = 1; xaiAlpha013 <= xaiAlpha014; xaiAlpha013++){
			String xaiAlpha004 ="";
			int xaiAlpha003 = Integer.parseInt(xaiAlpha006.readLine());
			int[] xaiAlpha010 = new int[xaiAlpha003];
			StringTokenizer xaiAlpha008 = new StringTokenizer(xaiAlpha006.readLine());
			for(int xaiAlpha002=0; xaiAlpha002<xaiAlpha003; xaiAlpha002++){
				xaiAlpha010[xaiAlpha002] = Integer.parseInt(xaiAlpha008.nextToken());
			}
			int xaiAlpha011 = 0;
			int xaiAlpha009 = 0;
			int xaiAlpha007 = 0;
			for(int xaiAlpha002=1; xaiAlpha002<xaiAlpha003; xaiAlpha002++){
				if(xaiAlpha010[xaiAlpha002]<xaiAlpha010[xaiAlpha002-1]){
					xaiAlpha011 += xaiAlpha010[xaiAlpha002-1] - xaiAlpha010[xaiAlpha002];
					xaiAlpha007 = Math.max(xaiAlpha007, xaiAlpha010[xaiAlpha002-1] - xaiAlpha010[xaiAlpha002]); 
				}
			}
			for(int xaiAlpha002=1; xaiAlpha002<xaiAlpha003; xaiAlpha002++){
				xaiAlpha009 += Math.min(xaiAlpha010[xaiAlpha002-1], xaiAlpha007);
			}
			// TODO Code goes here
			xaiAlpha012.write("Case #"+xaiAlpha013+": "+xaiAlpha011+" "+xaiAlpha009);
			xaiAlpha012.newLine();
		}
		xaiAlpha006.close();
		xaiAlpha005.close();
		xaiAlpha012.close();
	}
}