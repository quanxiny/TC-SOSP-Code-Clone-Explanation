import java.util.Arrays;
import java.util.Scanner;

public class Main {

	public static void main(String[] xaiAlpha000) {
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

		Scanner xaiAlpha005 = new Scanner(System.in);
		int xaiAlpha003 = xaiAlpha005.nextInt();
		int xaiAlpha002[] = new int[xaiAlpha003];
		for (int xaiAlpha004=0;xaiAlpha004<xaiAlpha003;xaiAlpha004++) {
			xaiAlpha002[xaiAlpha004] = xaiAlpha005.nextInt();
		}
		Arrays.parallelSort(xaiAlpha002);
		int xaiAlpha001 =0;
		for (int xaiAlpha004=0;xaiAlpha004<xaiAlpha003-1;xaiAlpha004++) {
			xaiAlpha001 +=xaiAlpha002[xaiAlpha004];
		}
		if (xaiAlpha001>xaiAlpha002[xaiAlpha003-1]) {
			System.out.println("Yes");
		} else {
			System.out.println("No");
		}
	}
}
