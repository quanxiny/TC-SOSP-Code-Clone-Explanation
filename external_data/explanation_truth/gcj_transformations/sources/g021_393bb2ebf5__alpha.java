package googlejam6.p339;
import java.io.*;
import java.util.*;

public class RankAndFile {
	public static void main(String[] xaiAlpha001) throws Exception {
		Scanner xaiAlpha011 = new Scanner(new FileReader(xaiAlpha001[0]));
		PrintWriter xaiAlpha003 = new PrintWriter(new FileWriter(xaiAlpha001[0]+".out.txt"));

		int xaiAlpha000 = xaiAlpha011.nextInt();
		List<Character> xaiAlpha007 = null;
		StringBuilder xaiAlpha008 = new StringBuilder();

		for (int xaiAlpha010 = 0; xaiAlpha010 < xaiAlpha000; xaiAlpha010++) {
			int xaiAlpha009 = xaiAlpha011.nextInt();
			int xaiAlpha004 = (2 * xaiAlpha009 - 1) * xaiAlpha009;
			TreeSet<Integer> xaiAlpha006 = new TreeSet<Integer>();

			for (int xaiAlpha002 = 0; xaiAlpha002 < xaiAlpha004; xaiAlpha002++) {
				int xaiAlpha005 = xaiAlpha011.nextInt();
				if (xaiAlpha006.contains(xaiAlpha005)) xaiAlpha006.remove(xaiAlpha005);
				else xaiAlpha006.add(xaiAlpha005);
			}
			xaiAlpha008.setLength(0);
			while (!xaiAlpha006.isEmpty()) {
				xaiAlpha008.append(' ');
				xaiAlpha008.append(xaiAlpha006.pollFirst());
			}
			xaiAlpha003.println("Case #" + (xaiAlpha010 + 1) + ":" + xaiAlpha008.toString());
		}

		xaiAlpha003.flush();
		xaiAlpha003.close();
		xaiAlpha011.close();
	}
}