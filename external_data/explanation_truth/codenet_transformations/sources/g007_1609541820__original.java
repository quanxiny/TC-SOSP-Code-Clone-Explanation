import java.util.*;

public class Main {
    public static void main(String[] args) {
        final Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] arr = new int[n];

        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }
        int sum = 0;
        int mx = -1;
        for (int i : arr) {
            sum += i;
            mx = Math.max(mx, i);
        }
        System.out.println((sum - mx > mx) ? "Yes" : "No");
        sc.close();
    }
}