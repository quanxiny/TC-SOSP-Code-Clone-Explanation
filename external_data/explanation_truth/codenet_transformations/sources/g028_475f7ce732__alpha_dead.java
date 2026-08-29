import java.util.*;

public class Main {
	public static void main(String[] xaiAlpha001) throws Exception{
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

		Scanner xaiAlpha006 = new Scanner(System.in);
		int xaiAlpha004 = xaiAlpha006.nextInt();
		int xaiAlpha000 = xaiAlpha006.nextInt();
      	int xaiAlpha003 = 0;
      	for(int xaiAlpha002=0; xaiAlpha002<=xaiAlpha004; ++xaiAlpha002){
        	for(int xaiAlpha005=0; xaiAlpha005<=xaiAlpha004; ++xaiAlpha005){
	    		if(xaiAlpha000>=xaiAlpha002+xaiAlpha005 && xaiAlpha000-(xaiAlpha002+xaiAlpha005)<=xaiAlpha004){
            		xaiAlpha003 = xaiAlpha003 + 1;
           		}
        	}
    	}
      	System.out.println(xaiAlpha003);
	}
}
