import java.util.*;

public class Main {

    public static void main(String xaiAlpha000[]) {
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }


        // 入力
        Scanner xaiAlpha009 = new Scanner(System.in);
        int xaiAlpha008 = Integer.parseInt(xaiAlpha009.next());
        int xaiAlpha004 = Integer.parseInt(xaiAlpha009.next());
        int xaiAlpha002 = Integer.parseInt(xaiAlpha009.next());
        int xaiAlpha001 = Integer.parseInt(xaiAlpha009.next());
        int xaiAlpha007 = Integer.parseInt(xaiAlpha009.next());
        xaiAlpha009.close();

        // 主処理
        int xaiAlpha003 = xaiAlpha008 * xaiAlpha001 + xaiAlpha004 * xaiAlpha007;
        int xaiAlpha006 = xaiAlpha002 * Math.max(xaiAlpha001, xaiAlpha007) * 2;

        int xaiAlpha010 = xaiAlpha001 > xaiAlpha007 ? xaiAlpha008 * (xaiAlpha001 - xaiAlpha007) + xaiAlpha002 * Math.min(xaiAlpha001, xaiAlpha007) * 2 : xaiAlpha004 * (xaiAlpha007 - xaiAlpha001) + xaiAlpha002 * Math.min(xaiAlpha001, xaiAlpha007) * 2;
        int xaiAlpha005 = Math.min(Math.min(xaiAlpha003, xaiAlpha006), xaiAlpha010);

        int xaiAlpha011 = xaiAlpha005;

        // 出力
        System.out.println(xaiAlpha011);
    }
}
