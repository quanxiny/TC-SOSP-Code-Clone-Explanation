import java.util.Scanner;

public class Main {

	public static void main(String[] xaiAlpha000){
		Scanner xaiAlpha006 = new Scanner(System.in);
		int xaiAlpha001 = xaiAlpha006.nextInt();
		int xaiAlpha005 = xaiAlpha006.nextInt();
		int xaiAlpha003 = xaiAlpha006.nextInt();
		int xaiAlpha002 =0;
		for(int xaiAlpha004=100;xaiAlpha004>=1;xaiAlpha004--) {
			if (xaiAlpha001%xaiAlpha004==0&&xaiAlpha005%xaiAlpha004==0) {
				xaiAlpha002 ++;
				if (xaiAlpha002 ==xaiAlpha003) {
					System.out.println(xaiAlpha004);
					return ;
				}
			}
		}
	}
}