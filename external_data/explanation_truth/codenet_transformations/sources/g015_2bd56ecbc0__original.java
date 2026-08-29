import java.util.Scanner;

public class Main {

	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);
		int N = sc.nextInt();
		int now = 0;
		int x =0;
		int y = 0;
		for (int i=0;i<N;i++) {
			int t = sc.nextInt();
			int xt = sc.nextInt();
			int yt = sc.nextInt();
			int cost = Math.abs(x-xt)+Math.abs(y-yt);
			if (cost>t-now) {
				System.out.println("No");
				return ;
			}
			if((t-now-cost)%2!=0) {
				System.out.println("No");
				return ;
			}
			x = xt;
			y = yt;
			now = t;
		}
		System.out.println("Yes");
	}
}
