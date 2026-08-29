import java.util.*;
 
public class Main {
	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);
		int A = sc.nextInt();
        int B = sc.nextInt();
        int K = sc.nextInt();
  
      int a[] = new int[100];//配列100まで格納している
      int n = 0;//問題に該当する二つの数値を割り切れる数値の個数を定義している
      for(int i=1; i<=Math.min(A,B); i++){//1から、入力するA.Bどちらかの最小数値までを繰り返していく
      if(A%i==0 && B%i==0){//A.Bどちらでも割れる数値i
        n+=1;//i=1なのでnに1ずつ加算していく
        a[n] =i;//if文の条件に合うiの個数をa[n]に代入する
        }
      }
     System.out.println(a[n-K+1]);//大きい方からK番目に該当する数値を見つけるための式,a[n-K+1]番目に格納されている数値
    }
}
        