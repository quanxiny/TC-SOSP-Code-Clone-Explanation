package googlejam1.p565;


import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.Scanner;

public class SolverMush {
	static PrintWriter xaiAlpha007;

	public static void main(String[] xaiAlpha000) throws NumberFormatException,
	IOException {
		xaiAlpha007 = new PrintWriter("output");
		Scanner xaiAlpha010 = new Scanner(new File("input"));
		int xaiAlpha006 = xaiAlpha010.nextInt();
		for (int xaiAlpha008 = 1; xaiAlpha008 <= xaiAlpha006; xaiAlpha008++) {
			int xaiAlpha005 = xaiAlpha010.nextInt();
			int[] xaiAlpha004 = new int[xaiAlpha005];
			int xaiAlpha001 = 0, res2 = 0;
			int xaiAlpha011 = 0;
			int xaiAlpha003 = xaiAlpha010.nextInt();
			xaiAlpha004[0] = xaiAlpha003;
			for (int xaiAlpha002 = 1; xaiAlpha002 < xaiAlpha005; xaiAlpha002++) {
				xaiAlpha004[xaiAlpha002] = xaiAlpha010.nextInt();
				int xaiAlpha009 = xaiAlpha003 - xaiAlpha004[xaiAlpha002];
				if (xaiAlpha009 > 0) {
					xaiAlpha001 += xaiAlpha009;
				}
				if (xaiAlpha009 > xaiAlpha011) {
					xaiAlpha011 = xaiAlpha009;
				}
				xaiAlpha003 = xaiAlpha004[xaiAlpha002];
			}
			for (int xaiAlpha002 = 0; xaiAlpha002 < xaiAlpha005 - 1; xaiAlpha002++) {
				res2 += Math.min(xaiAlpha011, xaiAlpha004[xaiAlpha002]);
			}
		
			SolverMush.xaiAlpha007.println("Case #" + xaiAlpha008 + ": " + xaiAlpha001 + " " + res2);
		}
		xaiAlpha007.flush();
	}

}
