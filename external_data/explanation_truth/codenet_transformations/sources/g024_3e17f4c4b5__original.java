import java.util.*;

public class Main{

    Scanner sc = new Scanner(System.in);
    long[] arr = new long[(int)1e5];

    public static void main(String[] args){
        new Main().run();
    }

    void run() {
        String a = sc.next();
        String b = sc.next();
        String c = sc.next();

        int s = 0;
        while (true) {
            if (s == 0) {
                if (a.length() == 0) {
                    System.out.println("A");
                    return;
                }
                if (a.charAt(0) == 'a') {
                    s = 0;
                } else if (a.charAt(0) == 'b') {
                    s = 1;
                } else {
                    s = 2;
                }
                a = a.substring(1, a.length());

            } else if (s == 1) {
                if (b.length() == 0) {
                    System.out.println("B");
                    return;
                }
                if (b.charAt(0) == 'a') {
                    s = 0;
                } else if (b.charAt(0) == 'b') {
                    s = 1;
                } else {
                    s = 2;
                }
                b = b.substring(1, b.length());
            } else {
                if (c.length() == 0) {
                    System.out.println("C");
                    return;
                }
                if (c.charAt(0) == 'a') {
                    s = 0;
                } else if (c.charAt(0) == 'b') {
                    s = 1;
                } else {
                    s = 2;
                }
                c = c.substring(1, c.length());
            }
        }

    }


}
