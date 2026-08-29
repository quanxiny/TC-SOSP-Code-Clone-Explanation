import java.util.*;
public class Main {
	public static void main(String[] xaiAlpha001){
		Scanner xaiAlpha005 = new Scanner(System.in);
		// 整数の入力
      	int xaiAlpha003 = xaiAlpha005.nextInt();
      	int xaiAlpha000 = xaiAlpha005.nextInt();
        int xaiAlpha004,j;
        int xaiAlpha002 = 0;

        for(xaiAlpha004 = 0;xaiAlpha004 <= xaiAlpha003;xaiAlpha004++){
	        for(j = 0;j <= xaiAlpha003;j++){
		        if(xaiAlpha000 - (xaiAlpha004 + j) >= 0 && xaiAlpha000 - (xaiAlpha004 + j) <= xaiAlpha003){
                  xaiAlpha002 += 1;
                }
        	}          
        }
      	System.out.print(xaiAlpha002);
      
    }
}