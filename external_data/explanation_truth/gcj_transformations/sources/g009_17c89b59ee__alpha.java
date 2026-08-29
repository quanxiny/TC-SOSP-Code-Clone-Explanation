package googlejam1.p380;


import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Scanner;

public class MushroomMonster {
	static String xaiAlpha007 = "data/gcj2015/1a/", PROBLEM = "A", SIZE = "large",
			ATTEMPT = "0";

	public static void main(String[] xaiAlpha000) throws NumberFormatException,
			IOException {
		String xaiAlpha012 = xaiAlpha007 + PROBLEM + "-" + SIZE;
		if (SIZE.equals("small"))
			xaiAlpha012 += "-attempt" + ATTEMPT;
		Scanner xaiAlpha008 = new Scanner(new File(xaiAlpha012 + ".in"));
		BufferedWriter xaiAlpha005 = new BufferedWriter(new FileWriter(xaiAlpha007 + PROBLEM
				+ "-" + SIZE + "-attempt" + ATTEMPT + ".out"));
		int xaiAlpha010 = xaiAlpha008.nextInt();
		xaiAlpha008.nextLine();
		for (int xaiAlpha009 = 0; xaiAlpha009 < xaiAlpha010; xaiAlpha009++) {
			int xaiAlpha004 = xaiAlpha008.nextInt();
			int[] xaiAlpha003 = new int[xaiAlpha004];
			for (int xaiAlpha001 = 0; xaiAlpha001 < xaiAlpha004; xaiAlpha001++) {
				xaiAlpha003[xaiAlpha001] = xaiAlpha008.nextInt();
			}
			// Strategy 1
			long xaiAlpha011 = 0;
			for (int xaiAlpha001 = 0; xaiAlpha001 < xaiAlpha004 - 1; xaiAlpha001++) {
				if (xaiAlpha003[xaiAlpha001] > xaiAlpha003[xaiAlpha001 + 1])
					xaiAlpha011 += xaiAlpha003[xaiAlpha001] - xaiAlpha003[xaiAlpha001 + 1];
			}
			// Strategy 2
			// First find the max decrease
			int xaiAlpha002 = 0;
			for (int xaiAlpha001 = 0; xaiAlpha001 < xaiAlpha004 - 1; xaiAlpha001++) {
				if (xaiAlpha003[xaiAlpha001] - xaiAlpha003[xaiAlpha001 + 1] > xaiAlpha002)
					xaiAlpha002 = xaiAlpha003[xaiAlpha001] - xaiAlpha003[xaiAlpha001 + 1];
			}
			// Then try eating
			long xaiAlpha006 = 0;
			for (int xaiAlpha001 = 0; xaiAlpha001 < xaiAlpha004 - 1; xaiAlpha001++) {
				if (xaiAlpha003[xaiAlpha001] > xaiAlpha002) {
					// eat only max
					xaiAlpha006 += xaiAlpha002;
				} else {
					// eat the remaining
					xaiAlpha006 += xaiAlpha003[xaiAlpha001];
				}
			}
			xaiAlpha005.write("Case #" + (xaiAlpha009 + 1) + ": " + xaiAlpha011 + " " + xaiAlpha006);
			xaiAlpha005.newLine();
		}
		xaiAlpha008.close();
		xaiAlpha005.close();
	}
}
