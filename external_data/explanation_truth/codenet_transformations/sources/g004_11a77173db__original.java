import java.util.*;
public class Main {
	public static void main(String[] args){
		Scanner sc = new Scanner(System.in);
		// 整数の入力
      	int k = sc.nextInt();
      	int s = sc.nextInt();
        int i,j;
        int count = 0;

        for(i = 0;i <= k;i++){
	        for(j = 0;j <= k;j++){
		        if(s - (i + j) >= 0 && s - (i + j) <= k){
                  count += 1;
                }
        	}          
        }
      	System.out.print(count);
      
    }
}