package googlejam6.p602;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.StringTokenizer;
          
public class Main2 {
	
	public static int xaiAlpha012, N, M;
	public static int[][] xaiAlpha003;
	public static int[][] xaiAlpha009;
	public static int[] xaiAlpha005;
	public static boolean[] xaiAlpha006;
	public static int xaiAlpha013;
	
    public static void main(String[] xaiAlpha007) throws IOException {
         
    	BufferedReader xaiAlpha004 = new BufferedReader(new InputStreamReader(System.in));
    	StringBuffer xaiAlpha008 = new StringBuffer();
    	
    	xaiAlpha012 = Integer.parseInt(xaiAlpha004.readLine());
    	
    	for(int xaiAlpha011 = 1 ; xaiAlpha011 <= xaiAlpha012 ; xaiAlpha011++){
    		xaiAlpha008.append("Case #"+xaiAlpha011+":" );
    		N = Integer.parseInt(xaiAlpha004.readLine());
    		M = 2*N-1;
    		xaiAlpha009 = new int[M][N];
    		int[] xaiAlpha001 = new int[2501];  
    		
    		for(int xaiAlpha010 = 0 ; xaiAlpha010 < M ; xaiAlpha010++){
    			StringTokenizer xaiAlpha002 = new StringTokenizer(xaiAlpha004.readLine());
    			
    			for(int xaiAlpha000 = 0 ; xaiAlpha000 < N ; xaiAlpha000++){
    				xaiAlpha009[xaiAlpha010][xaiAlpha000] = Integer.parseInt(xaiAlpha002.nextToken());
    				xaiAlpha001[xaiAlpha009[xaiAlpha010][xaiAlpha000]] += 1;
    			}
    		}
    		
    		for(int xaiAlpha010 = 0 ; xaiAlpha010 <= 2500 ; xaiAlpha010++){
    			if(xaiAlpha001[xaiAlpha010]%2 == 1){
    				xaiAlpha008.append(" ").append(xaiAlpha010);
    			}
    		}
    		xaiAlpha008.append("\n");
    	}
    	
    	System.out.println(xaiAlpha008);
	}
}