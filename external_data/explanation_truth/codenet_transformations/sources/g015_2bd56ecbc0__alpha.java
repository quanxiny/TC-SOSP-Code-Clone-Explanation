import java.util.Scanner;

public class Main {

	public static void main(String[] xaiAlpha000) {
		Scanner xaiAlpha008 = new Scanner(System.in);
		int xaiAlpha003 = xaiAlpha008.nextInt();
		int xaiAlpha010 = 0;
		int xaiAlpha001 =0;
		int xaiAlpha005 = 0;
		for (int xaiAlpha007=0;xaiAlpha007<xaiAlpha003;xaiAlpha007++) {
			int xaiAlpha009 = xaiAlpha008.nextInt();
			int xaiAlpha006 = xaiAlpha008.nextInt();
			int xaiAlpha002 = xaiAlpha008.nextInt();
			int xaiAlpha004 = Math.abs(xaiAlpha001-xaiAlpha006)+Math.abs(xaiAlpha005-xaiAlpha002);
			if (xaiAlpha004>xaiAlpha009-xaiAlpha010) {
				System.out.println("No");
				return ;
			}
			if((xaiAlpha009-xaiAlpha010-xaiAlpha004)%2!=0) {
				System.out.println("No");
				return ;
			}
			xaiAlpha001 = xaiAlpha006;
			xaiAlpha005 = xaiAlpha002;
			xaiAlpha010 = xaiAlpha009;
		}
		System.out.println("Yes");
	}
}
