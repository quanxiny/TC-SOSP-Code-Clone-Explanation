import java.util.*;

public class Main {
    public static void main(String[] xaiAlpha000) {
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

        final Scanner xaiAlpha005 = new Scanner(System.in);
        int xaiAlpha001 = xaiAlpha005.nextInt();
        int xaiAlpha004 = 1;
        int xaiAlpha002 = (int)1e6;
        boolean[] xaiAlpha003 = new boolean[xaiAlpha002];
        while (true) {
            if (xaiAlpha003[xaiAlpha001]) {
                break;
            }
            xaiAlpha003[xaiAlpha001] = true;
            if ((xaiAlpha001 & 1) == 1) xaiAlpha001 = 3 * xaiAlpha001 + 1;
            else xaiAlpha001 /= 2;
            xaiAlpha004 += 1;
        }
        System.out.println(xaiAlpha004);
        xaiAlpha005.close();
    }
}