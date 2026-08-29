package googlejam7.p301;
import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Scanner;

public class CloseMatch 
{
	public static void main(String[] xaiAlpha001) throws FileNotFoundException
	{
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

		Scanner xaiAlpha000 = new Scanner(new File("C:\\Users\\Adam\\Documents\\codejam\\B-small-attempt0.in"));

		int xaiAlpha005 = xaiAlpha000.nextInt();
		xaiAlpha000.nextLine();
		
		for (int xaiAlpha018 = 1; xaiAlpha018 <= xaiAlpha005; xaiAlpha018++)
		{
			String xaiAlpha006 = xaiAlpha000.nextLine();
			String xaiAlpha014[] = xaiAlpha006.split(" ");
			String xaiAlpha020 = xaiAlpha014[0];
			String xaiAlpha008 = xaiAlpha014[1];
			
			ArrayList<String> xaiAlpha016 = new ArrayList<String>();
			xaiAlpha016.add(xaiAlpha020);
			boolean xaiAlpha013 = false;
			while (!xaiAlpha013)
			{
				xaiAlpha013 = true;
				int xaiAlpha003 = 0;
				while (xaiAlpha003 < xaiAlpha016.size())
				{
					String xaiAlpha012 = xaiAlpha016.get(xaiAlpha003);
					if (xaiAlpha012.contains("?"))
					{
						
						xaiAlpha013 = false;
						String xaiAlpha004 = xaiAlpha012.substring(0, xaiAlpha012.indexOf("?"));
						String xaiAlpha002 = xaiAlpha012.substring(xaiAlpha012.indexOf("?") + 1);
						for (int xaiAlpha011 = 0; xaiAlpha011 < 10; xaiAlpha011++)
						{
							xaiAlpha016.add(xaiAlpha004 + xaiAlpha011 + xaiAlpha002);
						}
						xaiAlpha016.remove(xaiAlpha012);
					}
					else
					{
						xaiAlpha003++;
					}
				}
			}
			
			ArrayList<String> xaiAlpha010 = new ArrayList<String>();
			xaiAlpha010.add(xaiAlpha008);
			xaiAlpha013 = false;
			while (!xaiAlpha013)
			{
				xaiAlpha013 = true;
				int xaiAlpha003 = 0;
				while (xaiAlpha003 < xaiAlpha010.size())
				{
					String xaiAlpha012 = xaiAlpha010.get(xaiAlpha003);
					if (xaiAlpha012.contains("?"))
					{
						
						xaiAlpha013 = false;
						String xaiAlpha004 = xaiAlpha012.substring(0, xaiAlpha012.indexOf("?"));
						String xaiAlpha002 = xaiAlpha012.substring(xaiAlpha012.indexOf("?") + 1);
						for (int xaiAlpha011 = 0; xaiAlpha011 < 10; xaiAlpha011++)
						{
							xaiAlpha010.add(xaiAlpha004 + xaiAlpha011 + xaiAlpha002);
						}
						xaiAlpha010.remove(xaiAlpha012);
					}
					else
					{
						xaiAlpha003++;
					}
				}
			}
			
			ArrayList<Integer> xaiAlpha007 = new ArrayList<Integer>();
			
			for (String xaiAlpha021 : xaiAlpha016)
			{
				for (String xaiAlpha015 : xaiAlpha010)
				{
					int xaiAlpha019 = Math.abs(Integer.valueOf(xaiAlpha021) - Integer.valueOf(xaiAlpha015));
					
					if (!xaiAlpha007.contains(xaiAlpha019))
						xaiAlpha007.add(xaiAlpha019);
				}
			}
			
			Collections.sort(xaiAlpha007);
			
			if (xaiAlpha018 == 1)
			{
				//for (String strin : cperms)
				//	System.out.println("C: " + strin);
				
				//for (String strin : jperms)
				//	System.out.println("J: " + strin);
			}
			
			xaiAlpha013 = false;
			int xaiAlpha017 = 0;
			while (!xaiAlpha013 && xaiAlpha017 < xaiAlpha016.size())
			{
				int xaiAlpha009 = 0;
				
				while (!xaiAlpha013 && xaiAlpha009 < xaiAlpha010.size())
				{
//System.out.println("C is " + cperms.get(a) + ", J is " + jperms.get(b));
					int xaiAlpha019 = Math.abs(Integer.valueOf(xaiAlpha016.get(xaiAlpha017)) - Integer.valueOf(xaiAlpha010.get(xaiAlpha009)));
//System.out.println("case " + i + " diff is " + diff);
					if (xaiAlpha019 == xaiAlpha007.get(0))
					{
						xaiAlpha013 = true;
						System.out.println("Case #" + xaiAlpha018 + ": " + xaiAlpha016.get(xaiAlpha017) + " " + xaiAlpha010.get(xaiAlpha009));
					}
					else
					{
						xaiAlpha009++;
					}
				}
				
				xaiAlpha017++;
			}
		}
		

	}
}
