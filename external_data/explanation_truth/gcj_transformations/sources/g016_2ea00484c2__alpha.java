package googlejam1.p815;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class MushroomMonster{

	public static void main(String[] xaiAlpha000) throws IOException {
		BufferedReader xaiAlpha006 = new BufferedReader(new InputStreamReader(System.in));
		int xaiAlpha001 = Integer.parseInt(xaiAlpha006.readLine());
		for (int xaiAlpha010 = 0; xaiAlpha010 < xaiAlpha001; xaiAlpha010++) {
			int xaiAlpha007 = Integer.parseInt(xaiAlpha006.readLine());
			int xaiAlpha003 = 0; 
			int xaiAlpha009 = 0; 
			String[] xaiAlpha004 = xaiAlpha006.readLine().split(" ");
			int xaiAlpha012 = 0;
			for (int xaiAlpha002 = 1; xaiAlpha002 < xaiAlpha007; xaiAlpha002++) {
				int xaiAlpha008 = Integer.parseInt(xaiAlpha004[xaiAlpha002-1]);
				int xaiAlpha005 = Integer.parseInt(xaiAlpha004[xaiAlpha002]);
				if (xaiAlpha005<xaiAlpha008){
					int xaiAlpha011 = xaiAlpha008-xaiAlpha005;
					xaiAlpha003+=xaiAlpha011;
					if (xaiAlpha012<xaiAlpha011){
						xaiAlpha012=xaiAlpha011;
					}
				}
			}
			for (int xaiAlpha002 = 1; xaiAlpha002 < xaiAlpha007; xaiAlpha002++) {
				int xaiAlpha008 = Integer.parseInt(xaiAlpha004[xaiAlpha002-1]);
				int xaiAlpha005 = Integer.parseInt(xaiAlpha004[xaiAlpha002]);
				xaiAlpha009+=(xaiAlpha008-xaiAlpha005)<xaiAlpha012?Math.min(xaiAlpha008, xaiAlpha012):xaiAlpha012;
			}
			System.out.println("Case #"+(xaiAlpha010+1)+": "+xaiAlpha003+" "+xaiAlpha009);
		}
	}

}
