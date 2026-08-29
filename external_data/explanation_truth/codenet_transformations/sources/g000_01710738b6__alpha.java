import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;
public class Main {

	public static void main(String[] xaiAlpha001) {
		Scanner xaiAlpha004 = new Scanner(System.in);
		int xaiAlpha000 = xaiAlpha004.nextInt();
		Map<Integer,Integer> xaiAlpha003 = new HashMap<Integer,Integer>();
		int xaiAlpha002 = 1;

		xaiAlpha003.put(xaiAlpha000,0);

		while(true) {
			xaiAlpha002++;
			if(xaiAlpha000%2==0) {
				xaiAlpha000 = xaiAlpha000/2;
			}
			else {
				xaiAlpha000 = xaiAlpha000*3+1;
			}
			if(xaiAlpha003.containsKey(xaiAlpha000)) {
				System.out.println(xaiAlpha002);
				break;
			}
			else {
				xaiAlpha003.put(xaiAlpha000,0);
			}
		}
	}

}