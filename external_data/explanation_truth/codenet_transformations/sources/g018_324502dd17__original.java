

import java.util.Scanner;

public class Main {

	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);

		String str = sc.next();

		int indexA = 0;
		while(str.charAt(indexA) != 'A'){
			indexA++;
		}
		int indexB = str.length();
		while(str.charAt(indexB - 1) != 'Z'){
			indexB--;
		}

		System.out.println(indexB - indexA);
    }
}