import java.util.*;

public class Main{
	public static void main(String[] xaiAlpha000){
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

		Scanner xaiAlpha006 = new Scanner(System.in);
        long xaiAlpha002 = xaiAlpha006.nextLong();

        long xaiAlpha001 = xaiAlpha002;

        for(long xaiAlpha005 = 1; xaiAlpha005 <= Math.sqrt(xaiAlpha002); xaiAlpha005++){
          if(xaiAlpha002 % xaiAlpha005 != 0) continue;
          long xaiAlpha004 = String.valueOf(xaiAlpha005).length();
          long xaiAlpha003 = String.valueOf(xaiAlpha002 / xaiAlpha005).length();
          xaiAlpha001 = Math.min(xaiAlpha001, Math.max(xaiAlpha004, xaiAlpha003));
        }

        System.out.println(xaiAlpha001);
	}
}