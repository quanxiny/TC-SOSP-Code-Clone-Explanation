package googlejam8.p580;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.Arrays;
import java.util.StringTokenizer;


public class A {
	public static void main(String[] xaiAlpha001) throws IOException {
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

		BufferedReader xaiAlpha000= new BufferedReader(new FileReader("A-small-attempt2.in"));
		int xaiAlpha013= Integer.parseInt(xaiAlpha000.readLine());
		PrintWriter xaiAlpha008= new PrintWriter(new FileWriter("smallA.txt"));
		for(int xaiAlpha006=1; xaiAlpha006<=xaiAlpha013; xaiAlpha006++){
			int xaiAlpha004= Integer.parseInt(xaiAlpha000.readLine());
			int xaiAlpha003[]= new int [xaiAlpha004];
			StringTokenizer xaiAlpha007= new StringTokenizer(xaiAlpha000.readLine());
			xaiAlpha008.printf("Case #%d:",xaiAlpha006);
			for(int xaiAlpha012=0; xaiAlpha012<xaiAlpha004; xaiAlpha012++)
				xaiAlpha003[xaiAlpha012]= Integer.parseInt(xaiAlpha007.nextToken());
			int xaiAlpha009=0;
			int xaiAlpha010=0;
			int xaiAlpha014=0;
			int xaiAlpha011=0;
			int xaiAlpha002=0;
			do{
				xaiAlpha009=0;
				xaiAlpha010=0;
				xaiAlpha014=0;
				xaiAlpha011=0;
				xaiAlpha002=0;
				for(int xaiAlpha012=0; xaiAlpha012<xaiAlpha004; xaiAlpha012++){
					int xaiAlpha005= xaiAlpha003[xaiAlpha012];
					xaiAlpha002+=xaiAlpha005;
					if(xaiAlpha005>xaiAlpha009){
						xaiAlpha014= xaiAlpha009;
						xaiAlpha011= xaiAlpha010;
						xaiAlpha009=xaiAlpha005;
						xaiAlpha010=xaiAlpha012;
					}
					else
						if(xaiAlpha005>xaiAlpha014){
							xaiAlpha014=xaiAlpha005;
							xaiAlpha011=xaiAlpha012;
						}
				}
				//System.out.println(Arrays.toString(p));
				if(xaiAlpha009>0){
				xaiAlpha008.print(" "+((char)('A'+xaiAlpha010)));
				xaiAlpha009--;
				xaiAlpha003[xaiAlpha010]--;
				if(xaiAlpha014>xaiAlpha009 && xaiAlpha014>0 && xaiAlpha014-1<=(xaiAlpha002-2)/2.0 && xaiAlpha002!=3){
					xaiAlpha008.print(((char)('A'+xaiAlpha011)));
					xaiAlpha003[xaiAlpha011]--;
					continue;
				}
				if(xaiAlpha009-1<=(xaiAlpha002-2)/2.0 && xaiAlpha009>0 && xaiAlpha002!=3){
					xaiAlpha008.print(((char)('A'+xaiAlpha010)));
					xaiAlpha009--;
					xaiAlpha003[xaiAlpha010]--;
				}
				
				}
				
			}while(xaiAlpha002!=0);
			xaiAlpha008.println();
		}
		xaiAlpha008.flush();
		xaiAlpha008.close();
	}

}
