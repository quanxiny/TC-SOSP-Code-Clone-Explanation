import java.io.*;
import java.math.*;
import java.util.*;
public class Main {  
 
	public static void main(String[] xaiAlpha000) {
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }
  
		FastScanner xaiAlpha017 = new FastScanner(); //Input
		OutPut xaiAlpha019 = new OutPut(); //Output
		String xaiAlpha021 = xaiAlpha017.xaiAlpha020().toUpperCase();
		String xaiAlpha005 = xaiAlpha017.xaiAlpha020().toUpperCase();
		String xaiAlpha004 = xaiAlpha017.xaiAlpha020().toUpperCase();
		Queue<Character> xaiAlpha009 = new LinkedList<Character>();
		Queue<Character> xaiAlpha028 = new LinkedList<Character>();
		Queue<Character> xaiAlpha012 = new LinkedList<Character>();
		char xaiAlpha018 = 'A';
		String xaiAlpha016 = "";
		for (int xaiAlpha027 = 0; xaiAlpha027 < xaiAlpha021.length(); xaiAlpha027++) xaiAlpha009.add(xaiAlpha021.charAt(xaiAlpha027));
		for (int xaiAlpha027 = 0; xaiAlpha027 < xaiAlpha005.length(); xaiAlpha027++) xaiAlpha028.add(xaiAlpha005.charAt(xaiAlpha027));
		for (int xaiAlpha027 = 0; xaiAlpha027 < xaiAlpha004.length(); xaiAlpha027++) xaiAlpha012.add(xaiAlpha004.charAt(xaiAlpha027));
		while (true) {
			if (xaiAlpha018=='A') {
				if (xaiAlpha009.size()==0) {
					xaiAlpha016="A";
					break;
				}
				xaiAlpha018=xaiAlpha009.poll();
			}else if (xaiAlpha018=='B') {
				if (xaiAlpha028.size()==0) {
					xaiAlpha016="B";
					break;
				}
				xaiAlpha018=xaiAlpha028.poll();
			}else {
				if (xaiAlpha012.size()==0) {
					xaiAlpha016="C";
					break;
				}
				xaiAlpha018=xaiAlpha012.poll();
			}
			//O.pln(cur);
		}
		xaiAlpha019.pln(xaiAlpha016);
	}
	public static long xaiAlpha001(long xaiAlpha002, long xaiAlpha015) {long xaiAlpha016 = xaiAlpha002/xaiAlpha015; if (xaiAlpha002%xaiAlpha015!=0) 
	xaiAlpha016++; return xaiAlpha016;}
	public static long xaiAlpha011(long xaiAlpha021, long xaiAlpha005) {
		if (xaiAlpha021==0||xaiAlpha005==0) return Math.max(xaiAlpha021,xaiAlpha005);
		return xaiAlpha011(Math.min(xaiAlpha021, xaiAlpha005),Math.max(xaiAlpha021, xaiAlpha005)%Math.min(xaiAlpha021, xaiAlpha005));
	}
	public static long xaiAlpha023(long xaiAlpha022, long xaiAlpha025, long xaiAlpha029) {
		long xaiAlpha016=1;
		while (xaiAlpha025>0) {
			if (xaiAlpha025%2==1) xaiAlpha016*=xaiAlpha022;
			xaiAlpha025/=2;
			xaiAlpha022*=xaiAlpha022;
			xaiAlpha022%=xaiAlpha029;
			xaiAlpha016%=xaiAlpha029;
		}
		return xaiAlpha016;
	}
	public static long xaiAlpha007(long xaiAlpha002,long xaiAlpha029) {return xaiAlpha023(xaiAlpha002,xaiAlpha029-2,xaiAlpha029);}
	public static int xaiAlpha026(long xaiAlpha003) { //Returns number of bits within a number
		int xaiAlpha030 = 0;
		while (xaiAlpha003>0) {
			if (xaiAlpha003%2==1) xaiAlpha030++;
			xaiAlpha003/=2;
		}
		return xaiAlpha030;
	}
	static class FastScanner {
		BufferedReader xaiAlpha014=new BufferedReader(new InputStreamReader(System.in));
		StringTokenizer xaiAlpha010=new StringTokenizer("");
		String xaiAlpha020() {
			while (!xaiAlpha010.hasMoreTokens())
				try {
					xaiAlpha010=new StringTokenizer(xaiAlpha014.readLine());
				} catch (IOException xaiAlpha006) {
					xaiAlpha006.printStackTrace();
				}
			return xaiAlpha010.nextToken();
		}
		int xaiAlpha024() {return Integer.parseInt(xaiAlpha020());}
		long xaiAlpha013() {return Long.parseLong(xaiAlpha020());};
	}
	static class OutPut{
		PrintWriter xaiAlpha008 = new PrintWriter(System.out);
		void pln(double xaiAlpha003) {xaiAlpha008.println(xaiAlpha003);xaiAlpha008.flush();}
		void pln(boolean xaiAlpha003) {xaiAlpha008.println(xaiAlpha003);xaiAlpha008.flush();}
		void pln(int xaiAlpha003) {xaiAlpha008.println(xaiAlpha003);xaiAlpha008.flush();}
		void pln(long xaiAlpha003) {xaiAlpha008.println(xaiAlpha003);xaiAlpha008.flush();}
		void pln(String xaiAlpha003) {xaiAlpha008.println(xaiAlpha003);xaiAlpha008.flush();}
		void pln(char xaiAlpha003) {xaiAlpha008.println(xaiAlpha003);xaiAlpha008.flush();}
		void pln(StringBuilder xaiAlpha003) {xaiAlpha008.println(xaiAlpha003);xaiAlpha008.flush();}
		void pln(BigInteger xaiAlpha003) {xaiAlpha008.println(xaiAlpha003);xaiAlpha008.flush();}
		void p(int xaiAlpha003) {xaiAlpha008.print(xaiAlpha003);xaiAlpha008.flush();}
		void p(long xaiAlpha003) {xaiAlpha008.print(xaiAlpha003);xaiAlpha008.flush();}
		void p(String xaiAlpha003) {xaiAlpha008.print(xaiAlpha003);xaiAlpha008.flush();}
		void p(char xaiAlpha003) {xaiAlpha008.print(xaiAlpha003);xaiAlpha008.flush();}
		void p(StringBuilder xaiAlpha003) {xaiAlpha008.print(xaiAlpha003);xaiAlpha008.flush();}
		void p(BigInteger xaiAlpha003) {xaiAlpha008.print(xaiAlpha003);xaiAlpha008.flush();}
		void p(double xaiAlpha003) {xaiAlpha008.print(xaiAlpha003);xaiAlpha008.flush();}
		void p(boolean xaiAlpha003) {xaiAlpha008.print(xaiAlpha003);xaiAlpha008.flush();}
	}
}