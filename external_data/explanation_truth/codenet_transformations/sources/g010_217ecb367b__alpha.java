import java.util.Scanner;

public class Main {

	public static void main(String[] xaiAlpha000) {
		try (Scanner xaiAlpha003 = new Scanner(System.in)) {
			int xaiAlpha005 = xaiAlpha003.nextInt(), s = xaiAlpha003.nextInt();
			int xaiAlpha004 = 0;
			for (int xaiAlpha001 = 0; xaiAlpha001 <= Math.min(xaiAlpha005, s); xaiAlpha001++) {
				for (int xaiAlpha006 = Math.max(0, s - xaiAlpha001 - xaiAlpha005); xaiAlpha006 <= Math.min(xaiAlpha005, s - xaiAlpha001); xaiAlpha006++) {
					int xaiAlpha002 = s - xaiAlpha001 - xaiAlpha006;
					if ((xaiAlpha002 >= 0) && (xaiAlpha002 <= xaiAlpha005)) {
						xaiAlpha004++;
					}
				}
			}
			System.out.println(xaiAlpha004);
		}
	}
}
