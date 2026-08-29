import java.util.*;
class Main {
    public static void main(String[] xaiAlpha000){
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

        Scanner xaiAlpha005 = new Scanner(System.in);
        int xaiAlpha003 = Integer.parseInt(xaiAlpha005.next()),b=Integer.parseInt(xaiAlpha005.next()),c=Integer.parseInt(xaiAlpha005.next());
        int xaiAlpha001 = Integer.parseInt(xaiAlpha005.next()),y=Integer.parseInt(xaiAlpha005.next());
        long xaiAlpha002 = xaiAlpha003*xaiAlpha001+b*y;
        for(int xaiAlpha004=2;xaiAlpha004<=Math.max(xaiAlpha001,y)*2;xaiAlpha004=xaiAlpha004+2){
            xaiAlpha002 = Math.min(xaiAlpha002,xaiAlpha003*Math.max(0,(xaiAlpha001-xaiAlpha004/2))+b*Math.max(0,(y-xaiAlpha004/2))+c*xaiAlpha004);
        }
        System.out.println(xaiAlpha002);
    }
}