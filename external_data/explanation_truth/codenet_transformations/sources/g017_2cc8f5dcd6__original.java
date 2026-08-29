import java.util.*;

public class Main{
  public static void main(String[] args) {
    Scanner sc = new Scanner(System.in);
    int A = sc.nextInt();
    int B = sc.nextInt();
    int K = sc.nextInt();
    int i =Math.min(A,B),ans =0,count =0;
    while (true) {
      if(A % i == 0 && B % i == 0) count++;
      if(count == K) {
        ans = i;
        break;
      }
      i--;
    }
    System.out.println(ans);
  }
}