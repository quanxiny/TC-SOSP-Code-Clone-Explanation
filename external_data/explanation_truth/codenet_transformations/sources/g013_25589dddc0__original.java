

import java.util.Scanner;
import java.util.Stack;

public class Main {

	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);

		String s = sc.next();

		Stack<Character> stack = new Stack<Character>();

		for(int i = 0; i < s.length(); i++){
			char c = s.charAt(i);

			switch(c){
			case '1':
			case '0':
				stack.push(c);
				break;
			case 'B':
				if(!stack.isEmpty()){
					stack.pop();
				}
			}
		}

		String result = "";
		while(!stack.isEmpty()){
			result = stack.pop() + result;
		}

		System.out.println(result);
	}
}