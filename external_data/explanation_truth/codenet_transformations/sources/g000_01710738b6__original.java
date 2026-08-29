import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;
public class Main {

	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);
		int s = sc.nextInt();
		Map<Integer,Integer> a = new HashMap<Integer,Integer>();
		int count = 1;

		a.put(s,0);

		while(true) {
			count++;
			if(s%2==0) {
				s = s/2;
			}
			else {
				s = s*3+1;
			}
			if(a.containsKey(s)) {
				System.out.println(count);
				break;
			}
			else {
				a.put(s,0);
			}
		}
	}

}