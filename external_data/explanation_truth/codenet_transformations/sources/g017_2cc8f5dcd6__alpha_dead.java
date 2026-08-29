import java.util.*;

public class Main{
  public static void main(String[] xaiAlpha000) {
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

    Scanner xaiAlpha005 = new Scanner(System.in);
    int xaiAlpha001 = xaiAlpha005.nextInt();
    int xaiAlpha004 = xaiAlpha005.nextInt();
    int xaiAlpha002 = xaiAlpha005.nextInt();
    int xaiAlpha003 =Math.min(xaiAlpha001,xaiAlpha004),ans =0,count =0;
    while (true) {
      if(xaiAlpha001 % xaiAlpha003 == 0 && xaiAlpha004 % xaiAlpha003 == 0) count++;
      if(count == xaiAlpha002) {
        ans = xaiAlpha003;
        break;
      }
      xaiAlpha003--;
    }
    System.out.println(ans);
  }
}