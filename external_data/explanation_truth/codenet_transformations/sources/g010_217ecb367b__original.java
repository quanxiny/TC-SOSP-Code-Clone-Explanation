import java.util.Scanner;

public class Main {

	public static void main(String[] args) {
		try (Scanner scanner = new Scanner(System.in)) {
			int k = scanner.nextInt(), s = scanner.nextInt();
			int count = 0;
			for (int x = 0; x <= Math.min(k, s); x++) {
				for (int y = Math.max(0, s - x - k); y <= Math.min(k, s - x); y++) {
					int z = s - x - y;
					if ((z >= 0) && (z <= k)) {
						count++;
					}
				}
			}
			System.out.println(count);
		}
	}
}
