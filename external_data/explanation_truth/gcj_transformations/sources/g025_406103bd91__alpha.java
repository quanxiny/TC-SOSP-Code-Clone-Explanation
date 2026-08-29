package googlejam3.p147;

import java.io.*;
import java.util.*;

public class Solver {
    static Scanner xaiAlpha009;
    static Writer  xaiAlpha012;
    public static void main(String xaiAlpha000[]) {
        if(xaiAlpha000.length != 1){
            System.out.println("Please specify the input file");
            return;
        }

		String xaiAlpha015 = xaiAlpha000[0];
		File xaiAlpha001 = new File(xaiAlpha015);
		BufferedReader xaiAlpha005;

        if (!xaiAlpha001.exists()) {
            System.out.println("Couldn't find file "+xaiAlpha015);
            return;
        } else if (xaiAlpha001.isDirectory()) {
            System.out.println(xaiAlpha015+" is a directory");
            return;
        }

        try {
			xaiAlpha005 = new BufferedReader (new FileReader (xaiAlpha001));
			xaiAlpha009 = new Scanner(xaiAlpha005);
        } catch (IOException xaiAlpha010){
		    System.out.println("Problem reading " + xaiAlpha015 );
        }

        try {
            xaiAlpha012 = new BufferedWriter(
                        new OutputStreamWriter(
                            new FileOutputStream(xaiAlpha015+".out"), "utf-8"));
            int xaiAlpha013 = xaiAlpha009.nextInt();
			for(int xaiAlpha007=0; xaiAlpha007<xaiAlpha013; xaiAlpha007++){
			    int xaiAlpha006 = xaiAlpha009.nextInt();
			    int xaiAlpha003 = xaiAlpha009.nextInt();
			    int xaiAlpha016 = xaiAlpha009.nextInt();
			
			    int xaiAlpha004 = xaiAlpha003/xaiAlpha016; //will round down
			    int xaiAlpha011 = xaiAlpha003%xaiAlpha016;
			    int xaiAlpha008 = xaiAlpha004 + (xaiAlpha016-1) + ((xaiAlpha011!=0)?1:0);
			    int xaiAlpha014 = xaiAlpha004*(xaiAlpha006-1) + xaiAlpha008;
			
			    xaiAlpha012.write("Case #"+(xaiAlpha007+1)+": ");
			    xaiAlpha012.write(""+xaiAlpha014);
			    xaiAlpha012.write("\n");
			}
        } catch (IOException xaiAlpha002) {
            System.out.println("Couldn't open an output file");
            return;
        }

        try{
            xaiAlpha012.close();
            xaiAlpha009.close();
        } catch (IOException xaiAlpha002) {
        }
    }
}

