import java.util.*;
public class Main {
	public static void main(String[] xaiAlpha000){
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

		Scanner xaiAlpha005 = new Scanner(System.in);
		// 整数の入力
		String xaiAlpha003 = xaiAlpha005.next();
        String xaiAlpha001[] = xaiAlpha003.split("");
        String xaiAlpha002 = "";
     
        for(int xaiAlpha004 = 0; xaiAlpha004 < xaiAlpha003.length();xaiAlpha004++){
			if(xaiAlpha002.equals("") && xaiAlpha001[xaiAlpha004].equals("B")){
              
            }else{
              if(xaiAlpha001[xaiAlpha004].equals("0")){
                xaiAlpha002 += "0";
              }else if(xaiAlpha001[xaiAlpha004].equals("1")){
                xaiAlpha002 += "1";
              }else{
                xaiAlpha002 = xaiAlpha002.substring(0, xaiAlpha002.length()-1);
              }
            }
        }
      	System.out.println(xaiAlpha002);
 
    }
}