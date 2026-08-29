import java.util.*;

public class Main{
	public static void main(String[] args){
		Scanner sc = new Scanner(System.in);
        long n = sc.nextLong();

        long answer = n;

        for(long i = 1; i <= Math.sqrt(n); i++){
          if(n % i != 0) continue;
          long len1 = String.valueOf(i).length();
          long len2 = String.valueOf(n / i).length();
          answer = Math.min(answer, Math.max(len1, len2));
        }

        System.out.println(answer);
	}
}