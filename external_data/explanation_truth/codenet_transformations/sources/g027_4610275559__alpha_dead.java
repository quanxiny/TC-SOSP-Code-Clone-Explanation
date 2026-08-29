import java.util.Scanner;

public class Main {
    public static void main(String[] xaiAlpha000) {
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

        Scanner xaiAlpha006 = new Scanner(System.in);
        Long xaiAlpha001 = xaiAlpha006.nextLong();
        int xaiAlpha003 = (int) Math.round(Math.sqrt(xaiAlpha001));
        int xaiAlpha004 = Integer.MAX_VALUE;
        for(long xaiAlpha005 = 1L; xaiAlpha005<=xaiAlpha003; xaiAlpha005++) {
            if(xaiAlpha001%xaiAlpha005==0){
                long xaiAlpha002 = xaiAlpha001/xaiAlpha005;
//                System.out.println(a+" "+b);
                if(xaiAlpha004 > String.valueOf(Math.max(xaiAlpha005, xaiAlpha002)).length()){
                    xaiAlpha004 = String.valueOf(Math.max(xaiAlpha005, xaiAlpha002)).length();
                }
            }
        }
        System.out.println(xaiAlpha004);
    }
}