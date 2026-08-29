import java.util.Scanner;

public class Main {

	public static void main(String[] args) {

		Scanner scan = new Scanner(System.in);

		int A = scan.nextInt();
		int B = scan.nextInt();
		int K = scan.nextInt();
		for(int i = Math.min(A, B); i >= 1; i--) {
			if(A % i == 0 && B % i == 0) {
				K--;
				if(K == 0) {
					System.out.println(i);
				}
			} 
		}
	}
}