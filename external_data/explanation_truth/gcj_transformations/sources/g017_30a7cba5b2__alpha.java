package googlejam10.p167;


import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.util.Scanner;

public class RatherPerplexingShowdown {
	
	static final String xaiAlpha011 = "IMPOSSIBLE";
		
	public static void main(String[] xaiAlpha001) {
		try {
			Scanner xaiAlpha009 = new Scanner(new BufferedReader(new FileReader(new File("A-large.in")), 256 << 10));
			BufferedWriter xaiAlpha013 = new BufferedWriter(new FileWriter(new File("output.txt")), 256 << 10);

			int xaiAlpha012 = xaiAlpha009.nextInt();
			for (int xaiAlpha014 = 1; xaiAlpha014 <= xaiAlpha012; xaiAlpha014++) {
				int xaiAlpha005 = xaiAlpha009.nextInt();
				int xaiAlpha004 = 1 << xaiAlpha005;
				int xaiAlpha008 = xaiAlpha009.nextInt();
				int xaiAlpha002 = xaiAlpha009.nextInt();
				int xaiAlpha000 = xaiAlpha009.nextInt();
				
				String[] xaiAlpha017 = new String[xaiAlpha005+1];
				String[] xaiAlpha010 = new String[xaiAlpha005+1];
				String[] xaiAlpha015 = new String[xaiAlpha005+1];

				xaiAlpha017[0] = "P";
				xaiAlpha010[0] = "R";
				xaiAlpha015[0] = "S";
				
				for (int xaiAlpha018 = 1; xaiAlpha018 <= xaiAlpha005; xaiAlpha018++) {
					if (xaiAlpha017[xaiAlpha018-1].compareTo(xaiAlpha010[xaiAlpha018-1]) < 0)
						xaiAlpha017[xaiAlpha018] =  xaiAlpha017[xaiAlpha018-1] + xaiAlpha010[xaiAlpha018-1];
					else 
						xaiAlpha017[xaiAlpha018] =  xaiAlpha010[xaiAlpha018-1] + xaiAlpha017[xaiAlpha018-1];
					
					if (xaiAlpha010[xaiAlpha018-1].compareTo(xaiAlpha015[xaiAlpha018-1]) < 0)
						xaiAlpha010[xaiAlpha018] =  xaiAlpha010[xaiAlpha018-1] + xaiAlpha015[xaiAlpha018-1];
					else 
						xaiAlpha010[xaiAlpha018] =  xaiAlpha015[xaiAlpha018-1] + xaiAlpha010[xaiAlpha018-1];
					
					if (xaiAlpha017[xaiAlpha018-1].compareTo(xaiAlpha015[xaiAlpha018-1]) < 0)
						xaiAlpha015[xaiAlpha018] =  xaiAlpha017[xaiAlpha018-1] + xaiAlpha015[xaiAlpha018-1];
					else 
						xaiAlpha015[xaiAlpha018] =  xaiAlpha015[xaiAlpha018-1] + xaiAlpha017[xaiAlpha018-1];
				}
				
				String xaiAlpha019 = null;
				int xaiAlpha016 = 0, ap = 0, as = 0;
				for (int xaiAlpha018 = 0; xaiAlpha018 < xaiAlpha017[xaiAlpha005].length(); xaiAlpha018++) {
					char xaiAlpha006 = xaiAlpha017[xaiAlpha005].charAt(xaiAlpha018);
					if (xaiAlpha006 == 'P')
						ap++;
					else if (xaiAlpha006 == 'R')
						xaiAlpha016++;
					else if (xaiAlpha006 == 'S')
						as++;
				}
				if (xaiAlpha016 == xaiAlpha008 & as == xaiAlpha000 & ap == xaiAlpha002) {
					if (xaiAlpha019 == null || xaiAlpha019.compareTo(xaiAlpha017[xaiAlpha005]) > 0)
						xaiAlpha019 = xaiAlpha017[xaiAlpha005];
				}

				xaiAlpha016 = 0; ap = 0; as = 0;
				for (int xaiAlpha018 = 0; xaiAlpha018 < xaiAlpha010[xaiAlpha005].length(); xaiAlpha018++) {
					char xaiAlpha006 = xaiAlpha010[xaiAlpha005].charAt(xaiAlpha018);
					if (xaiAlpha006 == 'P')
						ap++;
					else if (xaiAlpha006 == 'R')
						xaiAlpha016++;
					else if (xaiAlpha006 == 'S')
						as++;
				}
				if (xaiAlpha016 == xaiAlpha008 & as == xaiAlpha000 & ap == xaiAlpha002) {
					if (xaiAlpha019 == null || xaiAlpha019.compareTo(xaiAlpha010[xaiAlpha005]) > 0)
						xaiAlpha019 = xaiAlpha010[xaiAlpha005];
				}
				
				xaiAlpha016 = 0; ap = 0; as = 0;
				for (int xaiAlpha018 = 0; xaiAlpha018 < xaiAlpha015[xaiAlpha005].length(); xaiAlpha018++) {
					char xaiAlpha006 = xaiAlpha015[xaiAlpha005].charAt(xaiAlpha018);
					if (xaiAlpha006 == 'P')
						ap++;
					else if (xaiAlpha006 == 'R')
						xaiAlpha016++;
					else if (xaiAlpha006 == 'S')
						as++;
				}
				if (xaiAlpha016 == xaiAlpha008 & as == xaiAlpha000 & ap == xaiAlpha002) {
					if (xaiAlpha019 == null || xaiAlpha019.compareTo(xaiAlpha015[xaiAlpha005]) > 0)
						xaiAlpha019 = xaiAlpha015[xaiAlpha005];
				}

				if (xaiAlpha019 == null)
					xaiAlpha019 = xaiAlpha011;
				xaiAlpha013.append("Case #" + xaiAlpha014 + ": " + xaiAlpha019);
				
				xaiAlpha013.append("\n");
			}
			xaiAlpha009.close();
			xaiAlpha013.close();
		}
		catch (RuntimeException xaiAlpha003) {
			throw xaiAlpha003;
		}
		catch (Exception xaiAlpha007) {
			System.err.println("Error:" + xaiAlpha007.getMessage());
		}
	}
}
