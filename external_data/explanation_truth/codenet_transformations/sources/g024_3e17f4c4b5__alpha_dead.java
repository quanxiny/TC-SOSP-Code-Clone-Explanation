import java.util.*;

public class Main{

    Scanner xaiAlpha006 = new Scanner(System.in);
    long[] xaiAlpha002 = new long[(int)1e5];

    public static void main(String[] xaiAlpha001){
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

        new Main().run();
    }

    void run() {
        String xaiAlpha005 = xaiAlpha006.next();
        String xaiAlpha004 = xaiAlpha006.next();
        String xaiAlpha003 = xaiAlpha006.next();

        int xaiAlpha000 = 0;
        while (true) {
            if (xaiAlpha000 == 0) {
                if (xaiAlpha005.length() == 0) {
                    System.out.println("A");
                    return;
                }
                if (xaiAlpha005.charAt(0) == 'a') {
                    xaiAlpha000 = 0;
                } else if (xaiAlpha005.charAt(0) == 'b') {
                    xaiAlpha000 = 1;
                } else {
                    xaiAlpha000 = 2;
                }
                xaiAlpha005 = xaiAlpha005.substring(1, xaiAlpha005.length());

            } else if (xaiAlpha000 == 1) {
                if (xaiAlpha004.length() == 0) {
                    System.out.println("B");
                    return;
                }
                if (xaiAlpha004.charAt(0) == 'a') {
                    xaiAlpha000 = 0;
                } else if (xaiAlpha004.charAt(0) == 'b') {
                    xaiAlpha000 = 1;
                } else {
                    xaiAlpha000 = 2;
                }
                xaiAlpha004 = xaiAlpha004.substring(1, xaiAlpha004.length());
            } else {
                if (xaiAlpha003.length() == 0) {
                    System.out.println("C");
                    return;
                }
                if (xaiAlpha003.charAt(0) == 'a') {
                    xaiAlpha000 = 0;
                } else if (xaiAlpha003.charAt(0) == 'b') {
                    xaiAlpha000 = 1;
                } else {
                    xaiAlpha000 = 2;
                }
                xaiAlpha003 = xaiAlpha003.substring(1, xaiAlpha003.length());
            }
        }

    }


}
