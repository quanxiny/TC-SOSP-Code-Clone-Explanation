package googlejam1.p199;


import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;



public class ProblemA {

	/**
	 * @param args
	 */
	public static void main(String[] xaiAlpha000) {

		//String filenameInput = "A-sample.in";
		//String filenameOutput = "A-sample.out";
		
		//String filenameInput = "A-small-attempt0.in";
		//String filenameOutput = "A-small-attempt0.out";
		
		
		String xaiAlpha009 = "A-large.in";
		String xaiAlpha005 = "A-large.out";

		Class xaiAlpha001 = ProblemA.class;
		try {

			String xaiAlpha010 = "src/"
					+ xaiAlpha001.getPackage().getName().replace(".", "/");
			BufferedReader xaiAlpha014 = new BufferedReader(new FileReader(new File(
					xaiAlpha010 + "/" + xaiAlpha009)));
			BufferedWriter xaiAlpha016 = new BufferedWriter(new FileWriter(new File(
					xaiAlpha010 + "/" + xaiAlpha005)));
			int xaiAlpha006 = Integer.parseInt(xaiAlpha014.readLine());
			// System.out.println("Number of Testcases: " + numOfTestcases);
			for (int xaiAlpha015 = 0; xaiAlpha015 < xaiAlpha006; xaiAlpha015++) {
				System.out.println("Testnumber : " + xaiAlpha015);
				int xaiAlpha007 = 0;
				int xaiAlpha011 = 0;
				int xaiAlpha002 = Integer.parseInt(xaiAlpha014.readLine());
				String[] xaiAlpha017 = xaiAlpha014.readLine().split(" ");
				int[] xaiAlpha008 = new int[xaiAlpha002];
				for (int xaiAlpha003=0;xaiAlpha003<xaiAlpha002;xaiAlpha003++) {
					xaiAlpha008[xaiAlpha003] = Integer.parseInt(xaiAlpha017[xaiAlpha003]);
				}
				int xaiAlpha012 = 0;
				for(int xaiAlpha003=0;xaiAlpha003<xaiAlpha002-1;xaiAlpha003++) {
					xaiAlpha007 += Math.max(0, xaiAlpha008[xaiAlpha003]-xaiAlpha008[xaiAlpha003+1]);
					xaiAlpha012  = Math.max(xaiAlpha012, xaiAlpha008[xaiAlpha003]-xaiAlpha008[xaiAlpha003+1]);
				}
				System.out.println(xaiAlpha012);
				for(int xaiAlpha003=0;xaiAlpha003<xaiAlpha002-1;xaiAlpha003++) {
					xaiAlpha011 += Math.min(xaiAlpha012, xaiAlpha008[xaiAlpha003]);
					System.out.println(xaiAlpha011 +" before " + xaiAlpha003);
				}
				
				String xaiAlpha013 = "Case #"
						+ (xaiAlpha015 + 1)
						+ ": "
						+ xaiAlpha007 + " " + xaiAlpha011;
				System.out.println(xaiAlpha013);

				if (xaiAlpha015 + 1 != xaiAlpha006) {
					xaiAlpha013 += "\n";
				}
				xaiAlpha016.write(xaiAlpha013);

			}

			xaiAlpha016.flush();
			xaiAlpha016.close();
		} catch (FileNotFoundException xaiAlpha004) {
			// TODO Auto-generated catch block
			xaiAlpha004.printStackTrace();
		} catch (IOException xaiAlpha004) {
			// TODO Auto-generated catch block
			xaiAlpha004.printStackTrace();
		} 

	}

}
