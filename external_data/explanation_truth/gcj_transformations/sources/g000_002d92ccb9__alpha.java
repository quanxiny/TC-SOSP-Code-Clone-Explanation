package googlejam1.p296;


import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class A {

	public static void main(String[] xaiAlpha000) throws FileNotFoundException {
		Scanner xaiAlpha010 = new Scanner(new File("C:\\Users\\Valentin\\workspace_luna\\CodeJam\\src\\A-large(1).in"));
		System.setOut(new PrintStream(new File("C:\\Users\\Valentin\\workspace_luna\\CodeJam\\src\\test.out")));

		int xaiAlpha011 = xaiAlpha010.nextInt();
		for (int xaiAlpha006 = 0; xaiAlpha006 < xaiAlpha011; xaiAlpha006++) {
			int xaiAlpha001 = xaiAlpha010.nextInt();
			List<Integer> xaiAlpha007 = new ArrayList<>();
			for (int xaiAlpha009 = 0; xaiAlpha009 < xaiAlpha001; xaiAlpha009++) {
				xaiAlpha007.add(xaiAlpha010.nextInt());
			}
			
			long xaiAlpha002 = 0;
			long xaiAlpha005 = 0;
			//normal
			int xaiAlpha008 = xaiAlpha007.get(0);
			for (int xaiAlpha009 = 1; xaiAlpha009 < xaiAlpha007.size(); xaiAlpha009++) {
				if (xaiAlpha008 > xaiAlpha007.get(xaiAlpha009)) {
					xaiAlpha002 += xaiAlpha008 - xaiAlpha007.get(xaiAlpha009);
				}
				xaiAlpha008 = xaiAlpha007.get(xaiAlpha009);
			}
			
			//special
			int xaiAlpha003 = -1;
			xaiAlpha008 = xaiAlpha007.get(0);
			for (int xaiAlpha009 = 1; xaiAlpha009 < xaiAlpha007.size(); xaiAlpha009++) {
				int xaiAlpha004 = xaiAlpha007.get(xaiAlpha009);
				if (xaiAlpha008 - xaiAlpha004 > xaiAlpha003) {
					xaiAlpha003 = xaiAlpha008 - xaiAlpha004;
				}
				xaiAlpha008 = xaiAlpha004;
			}
			
			for (int xaiAlpha009 = 1; xaiAlpha009 < xaiAlpha007.size(); xaiAlpha009++) {
				int xaiAlpha004 = xaiAlpha007.get(xaiAlpha009-1);
				xaiAlpha005 += Math.min(xaiAlpha003, xaiAlpha004);
			}
			System.out.println("Case #" + (xaiAlpha006+1) + ": " + xaiAlpha002 + " " + xaiAlpha005);
		}
	}

}
