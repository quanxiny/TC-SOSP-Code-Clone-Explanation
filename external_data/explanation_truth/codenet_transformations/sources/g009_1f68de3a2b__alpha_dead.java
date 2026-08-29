import java.util.Scanner;

public class Main {
    public static void main(String[] xaiAlpha001) {
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

        Scanner xaiAlpha010 = new Scanner(System.in);
        char[] xaiAlpha000 = xaiAlpha010.next().toCharArray();
        char[][] xaiAlpha008 = {{'d', 'r', 'e', 'a', 'm', 'e', 'r'},
                                {'e', 'r', 'a', 's', 'e', 'r'},
                                {'d', 'r', 'e', 'a', 'm'},
                                {'e', 'r', 'a', 's', 'e'}};

        for(int xaiAlpha009 = 0;xaiAlpha009 < xaiAlpha000.length / 2;xaiAlpha009++) {
            char xaiAlpha007 = xaiAlpha000[xaiAlpha009];
            xaiAlpha000[xaiAlpha009] = xaiAlpha000[xaiAlpha000.length - xaiAlpha009 - 1];
            xaiAlpha000[xaiAlpha000.length - xaiAlpha009 - 1] = xaiAlpha007;
        }

        for(int xaiAlpha009 = 0;xaiAlpha009 < 4;xaiAlpha009++) {
            for(int xaiAlpha002 = 0;xaiAlpha002 < xaiAlpha008[xaiAlpha009].length / 2;xaiAlpha002++) {
                char xaiAlpha007 = xaiAlpha008[xaiAlpha009][xaiAlpha002];
                xaiAlpha008[xaiAlpha009][xaiAlpha002] = xaiAlpha008[xaiAlpha009][xaiAlpha008[xaiAlpha009].length - xaiAlpha002 - 1];
                xaiAlpha008[xaiAlpha009][xaiAlpha008[xaiAlpha009].length - xaiAlpha002 - 1] = xaiAlpha007;
            }
        }

        int xaiAlpha009 = 0;
        boolean xaiAlpha003 = false;
        while(true) {
            boolean xaiAlpha005 = false;
            for(int xaiAlpha002 = 0;xaiAlpha002 < 4;xaiAlpha002++) {
                if(xaiAlpha009 + xaiAlpha008[xaiAlpha002].length > xaiAlpha000.length) continue;

                xaiAlpha005 = true;
                for(int xaiAlpha004 = 0;xaiAlpha004 < xaiAlpha008[xaiAlpha002].length;xaiAlpha004++) {
                    if(xaiAlpha000[xaiAlpha009 + xaiAlpha004] != xaiAlpha008[xaiAlpha002][xaiAlpha004]) {
                        xaiAlpha005 = false;
                        break;
                    }
                }

                if(xaiAlpha005) {
                    xaiAlpha009 += xaiAlpha008[xaiAlpha002].length;
                    break;
                }
            }

            if(xaiAlpha005 && xaiAlpha009 == xaiAlpha000.length) {
                xaiAlpha003 = true;
                break;
            }
            else if(!xaiAlpha005) {
                break;
            }
        }

        String xaiAlpha006 = xaiAlpha003 ? "YES" : "NO";
        System.out.println(xaiAlpha006);
    }
}