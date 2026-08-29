import java.util.*;

public class Main {
    public static void main(String[] xaiAlpha000) {
        final Scanner xaiAlpha006 = new Scanner(System.in);
        int xaiAlpha002 = xaiAlpha006.nextInt();
        int[] xaiAlpha003 = new int[xaiAlpha002];

        for (int xaiAlpha005 = 0; xaiAlpha005 < xaiAlpha002; xaiAlpha005++) {
            xaiAlpha003[xaiAlpha005] = xaiAlpha006.nextInt();
        }
        int xaiAlpha001 = 0;
        int xaiAlpha004 = -1;
        for (int xaiAlpha005 : xaiAlpha003) {
            xaiAlpha001 += xaiAlpha005;
            xaiAlpha004 = Math.max(xaiAlpha004, xaiAlpha005);
        }
        System.out.println((xaiAlpha001 - xaiAlpha004 > xaiAlpha004) ? "Yes" : "No");
        xaiAlpha006.close();
    }
}