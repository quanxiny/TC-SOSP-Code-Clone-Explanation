import java.util.*;
public class Main {
	public static void main(String[] args){
		Scanner sc = new Scanner(System.in);
		// 整数の入力
		String a[] = sc.next().split("");
        List<String> alist = new ArrayList<>();
        for(int i = 0;i < a.length;i++){
         alist.add(a[i]);
        }
      
        String b[] = sc.next().split("");
        List<String> blist = new ArrayList<>();
        for(int i = 0;i < b.length;i++){
         blist.add(b[i]);
        }
        String c[] = sc.next().split("");
        List<String> clist = new ArrayList<>();
        for(int i = 0;i < c.length;i++){
         clist.add(c[i]);
        }
      
      
        String check = "a";
      
       try{
          while(true){
          if(check.equals("a")){
            check = (String)alist.get(0);
            alist.remove(0);
          }else if(check.equals("b")){
            check = (String)blist.get(0);
            blist.remove(0);
          }else if(check.equals("c")){
            check = (String)clist.get(0);
            clist.remove(0);
          }
          }
        }catch(Exception e){
          
          System.out.println(check.toUpperCase());
        }
        
      
    }
}