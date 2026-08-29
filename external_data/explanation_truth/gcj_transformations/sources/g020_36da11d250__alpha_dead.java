package googlejam8.p653;
import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.Scanner;
import java.util.*;


public class SenateEvac {

	/**
	 * @param args
	 */
	public static void main(String[] xaiAlpha000) {
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

		
		File xaiAlpha005 = new File("e:\\Users\\Ricardo\\Documents\\CodeJam\\SenateEvac\\A-large.in");
		
		Scanner xaiAlpha003=null;
		try {
			xaiAlpha003 = new Scanner(xaiAlpha005);
		} catch (FileNotFoundException xaiAlpha002) {
			// TODO Auto-generated catch block
			xaiAlpha002.printStackTrace();
		}
		if (xaiAlpha003==null){
			return;
		}
		Integer xaiAlpha010 = xaiAlpha003.nextInt();
		xaiAlpha003.nextLine();

		for (Integer xaiAlpha007 = 0; xaiAlpha007 < xaiAlpha010; xaiAlpha007++) {
			Integer xaiAlpha004 = xaiAlpha003.nextInt();
			Integer xaiAlpha013 = 0;
			xaiAlpha003.nextLine();
			int[] xaiAlpha001 = new int[xaiAlpha004];
			System.out.print(String.format("Case #%d: ",xaiAlpha007+1));
			for(Character xaiAlpha006='A';xaiAlpha006<'A'+xaiAlpha004;xaiAlpha006++){
				Integer xaiAlpha012 = xaiAlpha003.nextInt();
				xaiAlpha001[xaiAlpha006 - 'A'] = xaiAlpha012;
				xaiAlpha013+=xaiAlpha012;
			}
			while(xaiAlpha013>0){
				ArrayList<Integer>evacuees =new ArrayList<Integer>();
				int xaiAlpha008 = -1;
				for (int xaiAlpha011=0;xaiAlpha011<xaiAlpha004;xaiAlpha011++){
					if (xaiAlpha001[xaiAlpha011]>0){
						//MUST evacuate
						if (xaiAlpha001[xaiAlpha011]>(xaiAlpha013-1)/2){
							evacuees.add(xaiAlpha011);
							if (evacuees.size()==2){
								break;
							}
						}			
						else{
							if (evacuees.size()==0){
								xaiAlpha008 = xaiAlpha011;
							}							
						}
					}
				}
				if (evacuees.size()==0){
					evacuees.add(xaiAlpha008);
				}
				for (Integer xaiAlpha009:evacuees){
					xaiAlpha001[xaiAlpha009]-=1;  
					System.out.print((char)( xaiAlpha009+'A'));
					xaiAlpha013--;
				}
				if (xaiAlpha013>0) System.out.print(" ");
			}
			System.out.println();
			if (xaiAlpha007+1<xaiAlpha010){
				xaiAlpha003.nextLine();
			}
		
		}

		xaiAlpha003.close();

	}

}
