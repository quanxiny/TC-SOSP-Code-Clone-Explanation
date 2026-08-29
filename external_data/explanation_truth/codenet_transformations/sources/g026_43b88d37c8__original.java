import java.util.Scanner;

public class Main {

	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);
		String s = sc.next();
		int position =0;
		while (position<s.length()) {
			if (position+5>s.length()) {
				System.out.println("NO");
				return ;
			}
			if ("dream".equals(s.substring(position,position+5))==false&&"erase".equals(s.substring(position,position+5))==false) {
				System.out.println("NO");
				return ;
			}
			position+=5;
			if (s.charAt(position-1)=='m') {
				if (position+2<=s.length()) {
					if ("er".equals(s.substring(position,position+2))==false ) {
						continue;
					}
					if (position+2<s.length()&&(s.charAt(position+2)=='e'||s.charAt(position+2)=='d')) {
						position +=2;
					} else if (position+2==s.length()){
						position +=2;
					}
				}
			} else {
				if (position<s.length()) {
					if (s.charAt(position)=='r') {
						position +=1;
					}
				}
			}

		}
		System.out.println("YES");
	}
}