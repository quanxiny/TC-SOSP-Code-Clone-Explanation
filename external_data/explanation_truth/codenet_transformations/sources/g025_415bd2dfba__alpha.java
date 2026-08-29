import java.util.*;
import java.util.Arrays;
public class Main {
    public static void main(String[] xaiAlpha000) throws Exception {
        Scanner xaiAlpha002 = new Scanner(System.in);
        
        int xaiAlpha004 = xaiAlpha002.nextInt();
        int xaiAlpha005 = xaiAlpha002.nextInt();
        int xaiAlpha006 = 0;
        
        int xaiAlpha003 = 0;
        for(int xaiAlpha007=0;xaiAlpha007<=xaiAlpha004;xaiAlpha007++){
            if(xaiAlpha007 != xaiAlpha005){
                for(int xaiAlpha001=0;xaiAlpha001<=xaiAlpha004;xaiAlpha001++){
                    if(xaiAlpha007+xaiAlpha001 != xaiAlpha005){
                        xaiAlpha006 = xaiAlpha005 - (xaiAlpha007+xaiAlpha001);
                        if(xaiAlpha006>=0 && xaiAlpha006<=xaiAlpha004){
                        //System.out.println("i:"+i+" j:"+j+"k:"+sub);
                        xaiAlpha003++;
                        
                        }
                    }else if(xaiAlpha007+xaiAlpha001 == xaiAlpha005)
                    {
                        //System.out.println("i:"+i+" j:"+j);
                        xaiAlpha003++;
                        break;
                    }
                }
                
            }else if(xaiAlpha007 == xaiAlpha005){
               // System.out.println("i:"+i);
                xaiAlpha003++;
            }
        }
        
        System.out.println(xaiAlpha003);
    }
}