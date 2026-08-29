package googlejam6.p340;


import java.io.File;
import java.io.PrintWriter;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Scanner;

/**
 * Created by popcorny on 4/16/16.
 */
public class RandAndFile {

    private final int[][] xaiAlpha006;
    private final int xaiAlpha002;

    public RandAndFile(int xaiAlpha002, int[][] xaiAlpha006) {
        this.xaiAlpha006 = xaiAlpha006;
        this.xaiAlpha002 = xaiAlpha002;
    }


    public static void main(String[] xaiAlpha000) throws Exception {
        Scanner xaiAlpha009;
        PrintWriter xaiAlpha014;
        String xaiAlpha015 = "randandfile";
        String xaiAlpha017 = "large";
        String xaiAlpha016   = String.format("quiz/%s/%s.in", xaiAlpha015, xaiAlpha017);
        String xaiAlpha019  = String.format("quiz/%s/%s.out", xaiAlpha015, xaiAlpha017);

        if (new File(xaiAlpha016).exists()) {
            xaiAlpha009 = new Scanner(new File(xaiAlpha016));
            if (xaiAlpha017.equals("sample")) {
                xaiAlpha014 = new PrintWriter(System.out);
            } else {
                xaiAlpha014 = new PrintWriter(xaiAlpha019);
            }
        } else {
            xaiAlpha009 = new Scanner(System.in);
            xaiAlpha014 = new PrintWriter(System.out);
        }


        int xaiAlpha020 = xaiAlpha009.nextInt();

        for (int xaiAlpha018 = 0; xaiAlpha018 < xaiAlpha020; xaiAlpha018++) {
            int xaiAlpha002 = xaiAlpha009.nextInt();

            int[][] xaiAlpha006 = new int[2*xaiAlpha002-1][xaiAlpha002];
            for (int xaiAlpha001=0; xaiAlpha001<2*xaiAlpha002-1; xaiAlpha001++) {

                for (int xaiAlpha010=0; xaiAlpha010<xaiAlpha002; xaiAlpha010++) {
                    int xaiAlpha012 = xaiAlpha009.nextInt();
                    xaiAlpha006[xaiAlpha001][xaiAlpha010] = xaiAlpha012;
                }
            }
			RandAndFile xaiAlpha005 = new RandAndFile(xaiAlpha002, xaiAlpha006);
			HashMap<Integer, Integer> xaiAlpha008 = new HashMap<>();
			
			for (int xaiAlpha007=0; xaiAlpha007<xaiAlpha005.xaiAlpha006.length; xaiAlpha007++) {
			    for (int xaiAlpha001=0; xaiAlpha001<xaiAlpha005.xaiAlpha002; xaiAlpha001++) {
			        int xaiAlpha012 = xaiAlpha005.xaiAlpha006[xaiAlpha007][xaiAlpha001];
			        if (xaiAlpha008.containsKey(xaiAlpha012)) {
			            xaiAlpha008.put(xaiAlpha012, xaiAlpha008.get(xaiAlpha012) + 1);
			        } else {
			            xaiAlpha008.put(xaiAlpha012, 1);
			        }
			    }
			}
			
			int[] xaiAlpha021 = new int[xaiAlpha005.xaiAlpha002];
			int xaiAlpha003=0;
			for (int xaiAlpha004: xaiAlpha008.keySet()) {
			    if (xaiAlpha008.get(xaiAlpha004) % 2 == 1) {
			        xaiAlpha021[xaiAlpha003++] = xaiAlpha004;
			    }
			}
			
			Arrays.sort(xaiAlpha021);

            int[] xaiAlpha011 = xaiAlpha021;
            xaiAlpha014.printf("Case #%d: ", xaiAlpha018 + 1);
            for(int xaiAlpha013=0;xaiAlpha013<xaiAlpha002;xaiAlpha013++) {
                xaiAlpha014.printf("%d ", xaiAlpha011[xaiAlpha013]);
            }
            xaiAlpha014.println();
        }
        xaiAlpha014.flush();
    }
}
