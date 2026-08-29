import java.util.Arrays;
import java.util.Scanner;

public class Main {

	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);
		int N = sc.nextInt();
		int L[] = new int[N];
		for (int i=0;i<N;i++) {
			L[i] = sc.nextInt();
		}
		Arrays.parallelSort(L);
		int sum =0;
		for (int i=0;i<N-1;i++) {
			sum +=L[i];
		}
		if (sum>L[N-1]) {
			System.out.println("Yes");
		} else {
			System.out.println("No");
		}
	}
}
