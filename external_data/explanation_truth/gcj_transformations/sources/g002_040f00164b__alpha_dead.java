package googlejam11.p101;
import java.util.Scanner;

public class B {
    public static void main(String[] xaiAlpha000) {
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

        Scanner xaiAlpha011 = new Scanner(System.in);
        int xaiAlpha007 = xaiAlpha011.nextInt();
        for (int xaiAlpha008 = 1; xaiAlpha008 <= xaiAlpha007; xaiAlpha008++) {
            int xaiAlpha005 = xaiAlpha011.nextInt();
            int xaiAlpha004 = xaiAlpha011.nextInt();
            double[] xaiAlpha002 = new double[xaiAlpha005];
            for (int xaiAlpha010 = 0; xaiAlpha010 < xaiAlpha005; xaiAlpha010++) {
                xaiAlpha002[xaiAlpha010] = xaiAlpha011.nextDouble();
            }

            double xaiAlpha006 = 0;
            for (long xaiAlpha003 = 0; xaiAlpha003 < (1 << xaiAlpha005); xaiAlpha003++) {
                if (Long.bitCount(xaiAlpha003) != xaiAlpha004) {
                    continue;
                }
                double xaiAlpha001 = 0;
                for (long xaiAlpha009 = xaiAlpha003; xaiAlpha009 != 0; xaiAlpha009 = ((xaiAlpha009 - 1) & xaiAlpha003)) {
                    if (Long.bitCount(xaiAlpha009) != xaiAlpha004 / 2) {
                        continue;
                    }
                    double xaiAlpha012 = 1;
                    for (int xaiAlpha010 = 0; xaiAlpha010 < xaiAlpha005; xaiAlpha010++) {
                        if ((xaiAlpha009 & (1 << xaiAlpha010)) != 0) {
                            xaiAlpha012 *= xaiAlpha002[xaiAlpha010];
                        } else if ((xaiAlpha003 & (1 << xaiAlpha010)) != 0) {
                            xaiAlpha012 *= (1 - xaiAlpha002[xaiAlpha010]);
                        }
                    }
                    xaiAlpha001 += xaiAlpha012;
                }
                xaiAlpha006 = Math.max(xaiAlpha001, xaiAlpha006);
            }
            System.out.print("Case #" + xaiAlpha008 + ": ");
            System.out.println(xaiAlpha006);
        }
        xaiAlpha011.close();
    }
}
