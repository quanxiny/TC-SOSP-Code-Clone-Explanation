package googlejam1.p164;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

public class Main {

	public static void main(String[] xaiAlpha001) throws IOException {
		BufferedReader xaiAlpha004 = new BufferedReader(new FileReader(new File("A.in")));
		PrintWriter xaiAlpha003 = new PrintWriter(new BufferedWriter(new FileWriter(new File("A.out"))));
		
		int xaiAlpha011 = Integer.parseInt(xaiAlpha004.readLine());
		for (int xaiAlpha010 = 0; xaiAlpha010 < xaiAlpha011; xaiAlpha010++) {
			int xaiAlpha006 = Integer.parseInt(xaiAlpha004.readLine());
			int[] xaiAlpha000 = new int[xaiAlpha006];
			String[] xaiAlpha005 = xaiAlpha004.readLine().split(" ");
			for (int xaiAlpha008 = 0; xaiAlpha008 < xaiAlpha006; xaiAlpha008++) xaiAlpha000[xaiAlpha008] = Integer.parseInt(xaiAlpha005[xaiAlpha008]);
			int xaiAlpha007 = 0, maxdiff = 0;
			for (int xaiAlpha008 = 1; xaiAlpha008 < xaiAlpha006; xaiAlpha008++) {
				int xaiAlpha009 = xaiAlpha000[xaiAlpha008-1]-xaiAlpha000[xaiAlpha008];
				if (xaiAlpha009 > 0) {
					xaiAlpha007 += xaiAlpha009;
					maxdiff = Math.max(maxdiff, xaiAlpha009);
				}
			}
			int xaiAlpha002 = 0;
			for (int xaiAlpha008 = 0; xaiAlpha008 < xaiAlpha006-1; xaiAlpha008++) xaiAlpha002 += Math.min(xaiAlpha000[xaiAlpha008], maxdiff);
			
			xaiAlpha003.println("Case #"+(xaiAlpha010+1)+": "+xaiAlpha007+" "+xaiAlpha002);
			xaiAlpha003.flush();
		}

		xaiAlpha003.close();
		xaiAlpha004.close();
	}
}
