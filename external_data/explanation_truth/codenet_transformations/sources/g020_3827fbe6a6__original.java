import java.util.*;
public class Main {
	public static void main(String[] args){
		Scanner sc = new Scanner(System.in);
		// 整数の入力
		String a = sc.next();
        String b[] = a.split("");
        String ans = "";
     
        for(int i = 0; i < a.length();i++){
			if(ans.equals("") && b[i].equals("B")){
              
            }else{
              if(b[i].equals("0")){
                ans += "0";
              }else if(b[i].equals("1")){
                ans += "1";
              }else{
                ans = ans.substring(0, ans.length()-1);
              }
            }
        }
      	System.out.println(ans);
 
    }
}