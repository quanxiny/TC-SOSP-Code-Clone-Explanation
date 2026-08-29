import java.util.Scanner;

public class Main {

	public static void main(String[] xaiAlpha000) {
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }


		Scanner xaiAlpha002 = new Scanner(System.in);

		int xaiAlpha001 = xaiAlpha002.nextInt();
		int xaiAlpha005 = xaiAlpha002.nextInt();
		int xaiAlpha003 = xaiAlpha002.nextInt();
		for(int xaiAlpha004 = Math.min(xaiAlpha001, xaiAlpha005); xaiAlpha004 >= 1; xaiAlpha004--) {
			if(xaiAlpha001 % xaiAlpha004 == 0 && xaiAlpha005 % xaiAlpha004 == 0) {
				xaiAlpha003--;
				if(xaiAlpha003 == 0) {
					System.out.println(xaiAlpha004);
				}
			} 
		}
	}
}