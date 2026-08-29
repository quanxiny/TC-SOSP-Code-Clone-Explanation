package googlejam8.p012;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Scanner;


public class Main {
	
	public static void main(String[] xaiAlpha000) throws IOException{
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

		Scanner xaiAlpha006 = new Scanner(System.in);
		//Scanner scanner = new Scanner(new FileInputStream(new File("A-small-attempt0.in")));
		//FileOutputStream fo = new FileOutputStream(new File("output.out"));
		int xaiAlpha013 = xaiAlpha006.nextInt();
		for(int xaiAlpha004 = 1; xaiAlpha004 <= xaiAlpha013; ++xaiAlpha004){
			int xaiAlpha002 = xaiAlpha006.nextInt();
			int[] xaiAlpha001 = new int[xaiAlpha002];
			for(int xaiAlpha012 = 0; xaiAlpha012 < xaiAlpha002; ++xaiAlpha012){
				xaiAlpha001[xaiAlpha012] = xaiAlpha006.nextInt();
			}
			System.out.print("Case #" + xaiAlpha004 + ":");
			//fo.write(("Case #" + x + ":").getBytes());
			if(xaiAlpha002 == 2){
				for(int xaiAlpha012 = 0; xaiAlpha012 < xaiAlpha001[0]; ++xaiAlpha012){
					System.out.print(" AB");
					//fo.write((" AB").getBytes());
				}
				System.out.println();
				//fo.write(("\n").getBytes());
			}
			else{
				int xaiAlpha011 = 0;
				for(int xaiAlpha009 = 0; xaiAlpha009 < xaiAlpha001.length; ++xaiAlpha009)
					if(xaiAlpha001[xaiAlpha009] != 0)
						++xaiAlpha011;
				int xaiAlpha007 = xaiAlpha011;
				while(xaiAlpha007 > 2){
					int xaiAlpha010 = 0;
					int xaiAlpha008 = -1;
					for(int xaiAlpha009 = 0; xaiAlpha009 < xaiAlpha001.length; ++xaiAlpha009){
						if(xaiAlpha001[xaiAlpha009] > xaiAlpha010){
							xaiAlpha010 = xaiAlpha001[xaiAlpha009];
							xaiAlpha008 = xaiAlpha009;
						}
					}
					int xaiAlpha003 = xaiAlpha008;
					--xaiAlpha001[xaiAlpha003];
					System.out.print(" " + (char)('A'+xaiAlpha003));
					int xaiAlpha014 = 0;
					for(int xaiAlpha012 = 0; xaiAlpha012 < xaiAlpha001.length; ++xaiAlpha012)
						if(xaiAlpha001[xaiAlpha012] != 0)
							++xaiAlpha014;
					//fo.write((" " + (char)('A'+index)).getBytes());
					xaiAlpha007 = xaiAlpha014;
				}
				int xaiAlpha005 = -1, i2 = -1;
				for(int xaiAlpha012 = 0; xaiAlpha012 < xaiAlpha001.length; ++xaiAlpha012){
					if(xaiAlpha001[xaiAlpha012] != 0){
						if(xaiAlpha005 == -1)
							xaiAlpha005 = xaiAlpha012;
						else
							i2 = xaiAlpha012;
					}
				}
				System.out.println(" " + (char)('A'+xaiAlpha005) + (char)('A'+i2));
				//fo.write((" " + (char)('A'+i1) + (char)('A'+i2) + '\n').getBytes());
			}
		}
		//fo.flush();
		//fo.close();
	}
	
}
