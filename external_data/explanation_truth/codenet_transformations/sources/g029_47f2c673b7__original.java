import java.util.*;

public class Main {

    public static void main(String args[]) {

        // 入力
        Scanner sc = new Scanner(System.in);
        int a = Integer.parseInt(sc.next());
        int b = Integer.parseInt(sc.next());
        int c = Integer.parseInt(sc.next());
        int x = Integer.parseInt(sc.next());
        int y = Integer.parseInt(sc.next());
        sc.close();

        // 主処理
        int normal = a * x + b * y;
        int half = c * Math.max(x, y) * 2;

        int comb = x > y ? a * (x - y) + c * Math.min(x, y) * 2 : b * (y - x) + c * Math.min(x, y) * 2;
        int price = Math.min(Math.min(normal, half), comb);

        int result = price;

        // 出力
        System.out.println(result);
    }
}
