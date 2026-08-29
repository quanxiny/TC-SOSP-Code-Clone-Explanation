import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        char[] s = sc.next().toCharArray();
        char[][] candidate = {{'d', 'r', 'e', 'a', 'm', 'e', 'r'},
                                {'e', 'r', 'a', 's', 'e', 'r'},
                                {'d', 'r', 'e', 'a', 'm'},
                                {'e', 'r', 'a', 's', 'e'}};

        for(int i = 0;i < s.length / 2;i++) {
            char tmp = s[i];
            s[i] = s[s.length - i - 1];
            s[s.length - i - 1] = tmp;
        }

        for(int i = 0;i < 4;i++) {
            for(int j = 0;j < candidate[i].length / 2;j++) {
                char tmp = candidate[i][j];
                candidate[i][j] = candidate[i][candidate[i].length - j - 1];
                candidate[i][candidate[i].length - j - 1] = tmp;
            }
        }

        int i = 0;
        boolean isSuccess = false;
        while(true) {
            boolean isSame = false;
            for(int j = 0;j < 4;j++) {
                if(i + candidate[j].length > s.length) continue;

                isSame = true;
                for(int k = 0;k < candidate[j].length;k++) {
                    if(s[i + k] != candidate[j][k]) {
                        isSame = false;
                        break;
                    }
                }

                if(isSame) {
                    i += candidate[j].length;
                    break;
                }
            }

            if(isSame && i == s.length) {
                isSuccess = true;
                break;
            }
            else if(!isSame) {
                break;
            }
        }

        String ans = isSuccess ? "YES" : "NO";
        System.out.println(ans);
    }
}