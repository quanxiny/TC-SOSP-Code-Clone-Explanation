package googlejam3.p120;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

public class A{
	
	static int xaiAlpha009,r,c,w,a;
	static String xaiAlpha003,str;
	static String[] xaiAlpha005;
	static boolean xaiAlpha002 = false;
	
	public static void main(String [ ] xaiAlpha001) throws IOException{
		int xaiAlpha008,j,k;
		
		
		BufferedReader xaiAlpha006 = new BufferedReader(new FileReader("A-large.in"));
	    try {
	    	File xaiAlpha004 = new File("aaa.out");
    		if (!xaiAlpha004.exists()) {
    			xaiAlpha004.createNewFile();
    		}
    		
    		FileWriter xaiAlpha000 = new FileWriter(xaiAlpha004.getAbsoluteFile());
    		BufferedWriter xaiAlpha007 = new BufferedWriter(xaiAlpha000);
    		
	        xaiAlpha003 = xaiAlpha006.readLine();
	        xaiAlpha009 = Integer.valueOf(xaiAlpha003); //1 <= T <= 100.

			
	        for(xaiAlpha008 = 0; xaiAlpha008 < xaiAlpha009; xaiAlpha008++){
				
				xaiAlpha003 = xaiAlpha006.readLine();
				xaiAlpha005 = xaiAlpha003.split("\\s");
				r = Integer.valueOf(xaiAlpha005[0]);
				c = Integer.valueOf(xaiAlpha005[1]);
				w = Integer.valueOf(xaiAlpha005[2]);
				
	        	//1 <= n <= 10^6.
				xaiAlpha002 = false;
				a=0;
				
				if (r == 1 && c==w) {
					a=w;
				} else if (w==1) {
					a=r*c;
				} else { // c>=w>1
					j = c%w; //>=0
					k = c/w; //>=1
					if(j==0){
						a = k*(r-1)+k + w-1;
					} else {
						a = k*(r-1)+k + w;
					}
				}
				
				if(xaiAlpha002) System.out.println("-------");
    			xaiAlpha007.write("Case #"+(xaiAlpha008+1)+": "+a+"\n");
	        }
	        
			xaiAlpha007.close();

	    } finally {
	        xaiAlpha006.close();
	    }
	}
}
