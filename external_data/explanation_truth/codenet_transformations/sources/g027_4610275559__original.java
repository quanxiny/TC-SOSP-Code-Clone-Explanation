import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        Long n = sc.nextLong();
        int to = (int) Math.round(Math.sqrt(n));
        int ans = Integer.MAX_VALUE;
        for(long a = 1L; a<=to; a++) {
            if(n%a==0){
                long b = n/a;
//                System.out.println(a+" "+b);
                if(ans > String.valueOf(Math.max(a, b)).length()){
                    ans = String.valueOf(Math.max(a, b)).length();
                }
            }
        }
        System.out.println(ans);
    }
}