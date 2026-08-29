import java.util.*;
import java.util.Arrays;
public class Main {
    public static void main(String[] args) throws Exception {
        Scanner scanner = new Scanner(System.in);
        
        int K = scanner.nextInt();
        int S = scanner.nextInt();
        int sub = 0;
        
        int count = 0;
        for(int i=0;i<=K;i++){
            if(i != S){
                for(int j=0;j<=K;j++){
                    if(i+j != S){
                        sub = S - (i+j);
                        if(sub>=0 && sub<=K){
                        //System.out.println("i:"+i+" j:"+j+"k:"+sub);
                        count++;
                        
                        }
                    }else if(i+j == S)
                    {
                        //System.out.println("i:"+i+" j:"+j);
                        count++;
                        break;
                    }
                }
                
            }else if(i == S){
               // System.out.println("i:"+i);
                count++;
            }
        }
        
        System.out.println(count);
    }
}