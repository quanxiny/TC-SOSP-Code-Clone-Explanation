import java.util.*;
 
public class Main {
	public static void main(String[] xaiAlpha000) {
		Scanner xaiAlpha007 = new Scanner(System.in);
		int xaiAlpha002 = xaiAlpha007.nextInt();
        int xaiAlpha006 = xaiAlpha007.nextInt();
        int xaiAlpha003 = xaiAlpha007.nextInt();
  
      int xaiAlpha004[] = new int[100];//配列100まで格納している
      int xaiAlpha001 = 0;//問題に該当する二つの数値を割り切れる数値の個数を定義している
      for(int xaiAlpha005=1; xaiAlpha005<=Math.min(xaiAlpha002,xaiAlpha006); xaiAlpha005++){//1から、入力するA.Bどちらかの最小数値までを繰り返していく
      if(xaiAlpha002%xaiAlpha005==0 && xaiAlpha006%xaiAlpha005==0){//A.Bどちらでも割れる数値i
        xaiAlpha001+=1;//i=1なのでnに1ずつ加算していく
        xaiAlpha004[xaiAlpha001] =xaiAlpha005;//if文の条件に合うiの個数をa[n]に代入する
        }
      }
     System.out.println(xaiAlpha004[xaiAlpha001-xaiAlpha003+1]);//大きい方からK番目に該当する数値を見つけるための式,a[n-K+1]番目に格納されている数値
    }
}
        