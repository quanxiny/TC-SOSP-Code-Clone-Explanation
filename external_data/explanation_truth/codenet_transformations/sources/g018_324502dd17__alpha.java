

import java.util.Scanner;

public class Main {

	public static void main(String[] xaiAlpha000) {
		Scanner xaiAlpha004 = new Scanner(System.in);

		String xaiAlpha003 = xaiAlpha004.next();

		int xaiAlpha002 = 0;
		while(xaiAlpha003.charAt(xaiAlpha002) != 'A'){
			xaiAlpha002++;
		}
		int xaiAlpha001 = xaiAlpha003.length();
		while(xaiAlpha003.charAt(xaiAlpha001 - 1) != 'Z'){
			xaiAlpha001--;
		}

		System.out.println(xaiAlpha001 - xaiAlpha002);
    }
}