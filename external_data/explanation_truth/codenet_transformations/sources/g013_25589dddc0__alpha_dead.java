

import java.util.Scanner;
import java.util.Stack;

public class Main {

	public static void main(String[] xaiAlpha001) {
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

		Scanner xaiAlpha005 = new Scanner(System.in);

		String xaiAlpha000 = xaiAlpha005.next();

		Stack<Character> xaiAlpha003 = new Stack<Character>();

		for(int xaiAlpha004 = 0; xaiAlpha004 < xaiAlpha000.length(); xaiAlpha004++){
			char xaiAlpha002 = xaiAlpha000.charAt(xaiAlpha004);

			switch(xaiAlpha002){
			case '1':
			case '0':
				xaiAlpha003.push(xaiAlpha002);
				break;
			case 'B':
				if(!xaiAlpha003.isEmpty()){
					xaiAlpha003.pop();
				}
			}
		}

		String xaiAlpha006 = "";
		while(!xaiAlpha003.isEmpty()){
			xaiAlpha006 = xaiAlpha003.pop() + xaiAlpha006;
		}

		System.out.println(xaiAlpha006);
	}
}