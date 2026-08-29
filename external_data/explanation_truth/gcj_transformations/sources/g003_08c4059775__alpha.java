package googlejam3.p212;


import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.OutputStreamWriter;

public class Q1 {

    public static void main(String[] xaiAlpha000) throws IOException {
        BufferedReader xaiAlpha006 = new BufferedReader(new FileReader(new File(xaiAlpha000[0])));
        BufferedWriter xaiAlpha007 = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(new File(xaiAlpha000[1]))));
        int xaiAlpha002 = Integer.parseInt(xaiAlpha006.readLine());


        for (int xaiAlpha008 = 0; xaiAlpha008 < xaiAlpha002; ++xaiAlpha008) {
            String[] xaiAlpha009 = xaiAlpha006.readLine().split("\\s+");
            long xaiAlpha001 = Long.parseLong(xaiAlpha009[0]);
            long xaiAlpha004 = Long.parseLong(xaiAlpha009[1]);
            long xaiAlpha003 = Long.parseLong(xaiAlpha009[2]);

            long xaiAlpha005 = xaiAlpha001 * new Double(Math.floor(xaiAlpha004 / xaiAlpha003 * 1.0)).intValue() + xaiAlpha003 - 1;

            if (xaiAlpha004 % xaiAlpha003 > 0) {
                xaiAlpha005 += 1;
            }

            // if (Width == Columns || Columns == 1)
            // res -= 1;
            // int time = new Double(Math.ceil(Math.log(max) / Math.log(2)) + 1).intValue();
            xaiAlpha007.write("Case #" + (xaiAlpha008 + 1) + ": " + xaiAlpha005 + "\n");
        }

        xaiAlpha006.close();
        xaiAlpha007.close();
    }

}
