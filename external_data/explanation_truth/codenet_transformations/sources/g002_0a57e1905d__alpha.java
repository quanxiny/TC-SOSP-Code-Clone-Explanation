import java.util.Scanner;

public class Main {

	public static void main(String[] xaiAlpha001) {
		try (Scanner xaiAlpha002 = new Scanner(System.in)) {
			String xaiAlpha000 = xaiAlpha002.next();
			System.out.println(xaiAlpha000.lastIndexOf('Z') - xaiAlpha000.indexOf('A') + 1);
		}
	}
}
