import java.util.*;

public class Main {
    public static void main(String[] xaiAlpha000) throws Exception {
        
        Scanner xaiAlpha003 = new Scanner(System.in);
        long xaiAlpha005 = xaiAlpha003.nextLong();
        int xaiAlpha001 = (int)Math.sqrt(xaiAlpha005);
        int xaiAlpha002 = 0;
        
        for(int xaiAlpha006=1; xaiAlpha006<=xaiAlpha001; xaiAlpha006++){
            if(xaiAlpha005%xaiAlpha006==0){
                xaiAlpha002 = xaiAlpha006;
            }
        }
        
        xaiAlpha005 /= xaiAlpha002;
        
        int xaiAlpha004 = String.valueOf(xaiAlpha005).length();
        int xaiAlpha007 = String.valueOf(xaiAlpha002).length();
        
        if(xaiAlpha007<=xaiAlpha004){
            System.out.println(xaiAlpha004);
        }else{
            System.out.println(xaiAlpha007);
        }
        
        
    }
}
