import java.io.*;
import java.math.*;
import java.util.*;
public class Main { 

	public static void main(String[] args) { 
		Scanner input = new Scanner(System.in); 
		String S = input.next();
		int N = S.length();
		int curSTART=0;
		boolean bad=false;
		while (curSTART<N) {
			if (curSTART+5<=N) {
				String test = S.substring(curSTART,curSTART+5);
				if (test.equals("dream")) {
					curSTART+=5;
					if (curSTART+2<=N) {
						if (S.substring(curSTART,curSTART+2).equals("er")) {
							curSTART+=2;
						}
					}
					if (curSTART+1<=N) {
						if (S.substring(curSTART,curSTART+1).equals("a")) {
							curSTART-=2;
							//Reset due to erase word being after dream 
							//(not dreamer)
						}
					}
				}else if (test.equals("erase")) {
					curSTART+=5;
					if (curSTART<N) {
						if (S.charAt(curSTART)=='r') curSTART++;
					}
				}else {
					bad=true;
				}
			}else {
				if (N-curSTART>1) {
					bad=true;
					break;
				} 
			}
			if (bad) break;
		}
		System.out.println(bad?"NO":"YES");
	}	
}