import java.util.*;
class Main {
    public static void main(String[] args){
        Scanner sc = new Scanner(System.in);
        int a = Integer.parseInt(sc.next()),b=Integer.parseInt(sc.next()),c=Integer.parseInt(sc.next());
        int x = Integer.parseInt(sc.next()),y=Integer.parseInt(sc.next());
        long ans = a*x+b*y;
        for(int i=2;i<=Math.max(x,y)*2;i=i+2){
            ans = Math.min(ans,a*Math.max(0,(x-i/2))+b*Math.max(0,(y-i/2))+c*i);
        }
        System.out.println(ans);
    }
}