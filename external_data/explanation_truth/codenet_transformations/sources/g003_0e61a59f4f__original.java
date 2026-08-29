import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        
        Scanner scanner = new Scanner(System.in);
        long N = scanner.nextLong();
        int n = (int)Math.sqrt(N);
        int X = 0;
        
        for(int i=1; i<=n; i++){
            if(N%i==0){
                X = i;
            }
        }
        
        N /= X;
        
        int valLenN = String.valueOf(N).length();
        int valLenX = String.valueOf(X).length();
        
        if(valLenX<=valLenN){
            System.out.println(valLenN);
        }else{
            System.out.println(valLenX);
        }
        
        
    }
}
