import java.util.Scanner;

public class Main {

	public static void main(String[] xaiAlpha001) {
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

		Scanner xaiAlpha003 = new Scanner(System.in);
		String xaiAlpha000 = xaiAlpha003.next();
		int xaiAlpha002 =0;
		while (xaiAlpha002<xaiAlpha000.length()) {
			if (xaiAlpha002+5>xaiAlpha000.length()) {
				System.out.println("NO");
				return ;
			}
			if ("dream".equals(xaiAlpha000.substring(xaiAlpha002,xaiAlpha002+5))==false&&"erase".equals(xaiAlpha000.substring(xaiAlpha002,xaiAlpha002+5))==false) {
				System.out.println("NO");
				return ;
			}
			xaiAlpha002+=5;
			if (xaiAlpha000.charAt(xaiAlpha002-1)=='m') {
				if (xaiAlpha002+2<=xaiAlpha000.length()) {
					if ("er".equals(xaiAlpha000.substring(xaiAlpha002,xaiAlpha002+2))==false ) {
						continue;
					}
					if (xaiAlpha002+2<xaiAlpha000.length()&&(xaiAlpha000.charAt(xaiAlpha002+2)=='e'||xaiAlpha000.charAt(xaiAlpha002+2)=='d')) {
						xaiAlpha002 +=2;
					} else if (xaiAlpha002+2==xaiAlpha000.length()){
						xaiAlpha002 +=2;
					}
				}
			} else {
				if (xaiAlpha002<xaiAlpha000.length()) {
					if (xaiAlpha000.charAt(xaiAlpha002)=='r') {
						xaiAlpha002 +=1;
					}
				}
			}

		}
		System.out.println("YES");
	}
}