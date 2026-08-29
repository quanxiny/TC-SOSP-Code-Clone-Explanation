package googlejam3.p280;


import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;

public class Q1 {

	public static void main(String[] xaiAlpha000) throws Exception {
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

		String xaiAlpha006 = "D:\\Work\\eclipse\\workspace\\CodeJam2015\\src\\round1c\\q1\\";
		String xaiAlpha003 = "A-large";
		//String fileName = "testA";
		File xaiAlpha007 = new File(xaiAlpha006 + xaiAlpha003 + ".in");
		File xaiAlpha009 = new File(xaiAlpha006 + xaiAlpha003 + ".out");
		BufferedReader xaiAlpha011 = new BufferedReader(new FileReader(xaiAlpha007));
		BufferedWriter xaiAlpha015 = new BufferedWriter(new FileWriter(xaiAlpha009));
		int xaiAlpha017 = Integer.parseInt(xaiAlpha011.readLine());
		for (int xaiAlpha018 = 1; xaiAlpha018 <= xaiAlpha017; xaiAlpha018++) {
			/*
			 * Your code here
			 */
			String xaiAlpha004 = xaiAlpha011.readLine();
			String[] xaiAlpha013 = xaiAlpha004.split(" ");
			
			xaiAlpha012 = Integer.parseInt(xaiAlpha013[0]);
			xaiAlpha010 = Integer.parseInt(xaiAlpha013[1]);
			xaiAlpha019 = Integer.parseInt(xaiAlpha013[2]);
			
			int xaiAlpha016 = xaiAlpha010 / xaiAlpha019;
			int xaiAlpha008 = xaiAlpha019;
			if (xaiAlpha010 % xaiAlpha019 == 0) {
				xaiAlpha008--;
			}
			
			int xaiAlpha005 = (xaiAlpha010 / xaiAlpha019) * (xaiAlpha012 - 1);
			int xaiAlpha002 = xaiAlpha005 + xaiAlpha016 + xaiAlpha008;
			String xaiAlpha001 = xaiAlpha002 + "";

			String xaiAlpha014 = "Case #" + xaiAlpha018 + ": " + xaiAlpha001 + "\n";
			xaiAlpha015.write(xaiAlpha014);

			//System.out.println(input1 + "//");
			//System.out.println(response);
		}
		xaiAlpha011.close();
		xaiAlpha015.close();
	}

	static int xaiAlpha012;
	static int xaiAlpha010;
	static int xaiAlpha019;
}
