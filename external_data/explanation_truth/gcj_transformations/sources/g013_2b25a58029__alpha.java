package googlejam2.p234;


import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.Queue;
import java.util.Scanner;

public class A {

	static Scanner xaiAlpha003;
	static PrintWriter xaiAlpha010;
	
	public static void main(String[] xaiAlpha000) throws IOException {
		xaiAlpha003 = new Scanner(new FileReader("input"));
		xaiAlpha010 = new PrintWriter(new FileWriter("output"));
		int xaiAlpha007 = xaiAlpha003.nextInt();
		for(int xaiAlpha006 = 1; xaiAlpha006 <= xaiAlpha007; xaiAlpha006++) {
			int xaiAlpha002 = xaiAlpha003.nextInt();
			Queue<Integer> xaiAlpha005 = new LinkedList<>();
			xaiAlpha005.add(0);
			int[] xaiAlpha001 = new int[xaiAlpha002 + 1];
			Arrays.fill(xaiAlpha001, Integer.MAX_VALUE);
			xaiAlpha001[0] = 0;
			while(xaiAlpha001[xaiAlpha002] == Integer.MAX_VALUE) {
				int xaiAlpha008 = xaiAlpha005.poll();
				if(xaiAlpha008 + 1 <= xaiAlpha002 && xaiAlpha001[xaiAlpha008 + 1] == Integer.MAX_VALUE) {
					xaiAlpha001[xaiAlpha008 + 1] = 1 + xaiAlpha001[xaiAlpha008];
					xaiAlpha005.add(xaiAlpha008 + 1);
				}
				StringBuilder xaiAlpha009 = new StringBuilder();
				xaiAlpha009.append(xaiAlpha008);
				xaiAlpha009 = xaiAlpha009.reverse();
				int xaiAlpha004 = Integer.parseInt(xaiAlpha009.toString());
				if(xaiAlpha004 <= xaiAlpha002 && xaiAlpha001[xaiAlpha004] == Integer.MAX_VALUE) {
					xaiAlpha001[xaiAlpha004] = 1 + xaiAlpha001[xaiAlpha008];
					xaiAlpha005.add(xaiAlpha004);
				}
			}
			xaiAlpha010.printf("Case #%d: %d\n", xaiAlpha006, xaiAlpha001[xaiAlpha002]);
		}
		xaiAlpha010.close();
		xaiAlpha003.close();
	}
	
}
