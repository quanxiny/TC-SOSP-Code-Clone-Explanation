import java.util.*;

public class Main {
    public static void main(String[] args) {
        final Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int ans = 1;
        int MAXN = (int)1e6;
        boolean[] present = new boolean[MAXN];
        while (true) {
            if (present[n]) {
                break;
            }
            present[n] = true;
            if ((n & 1) == 1) n = 3 * n + 1;
            else n /= 2;
            ans += 1;
        }
        System.out.println(ans);
        sc.close();
    }
}