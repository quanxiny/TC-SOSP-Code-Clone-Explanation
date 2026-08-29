import java.util.*;

public class Main {

    public static void main(String xaiAlpha001[]) {

        // 入力
        Scanner xaiAlpha004 = new Scanner(System.in);
        String xaiAlpha000 = xaiAlpha004.next();
        xaiAlpha004.close();

        // 主処理
        String xaiAlpha003 = xaiAlpha000.replace("eraser", "").replace("erase", "").replace("dreamer", "").replace("dream", "");
        boolean xaiAlpha002 = xaiAlpha003.length() == 0;
        String xaiAlpha005 = xaiAlpha002 ? "YES" : "NO";

        // 出力
        System.out.println(xaiAlpha005);
    }
}
