import java.util.*;

public class Main {
	public static void main(String[] args) throws Exception{
		Scanner scn = new Scanner(System.in);
		int k = scn.nextInt();
		int s = scn.nextInt();
      	int count = 0;
      	for(int x=0; x<=k; ++x){
        	for(int y=0; y<=k; ++y){
	    		if(s>=x+y && s-(x+y)<=k){
            		count = count + 1;
           		}
        	}
    	}
      	System.out.println(count);
	}
}
