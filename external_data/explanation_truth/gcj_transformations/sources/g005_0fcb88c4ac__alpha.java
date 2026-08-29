package googlejam10.p195;


import java.io.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Scanner;

public class TaskA {
    public static void main(String[] xaiAlpha001) {
        String xaiAlpha003 = "A-small-attempt1.in";
        try (BufferedReader xaiAlpha014 = new BufferedReader(new FileReader(xaiAlpha003))) {

            try (BufferedWriter xaiAlpha017 = new BufferedWriter(new FileWriter(xaiAlpha003 + ".out"))) {
                int xaiAlpha010 = Integer.valueOf(xaiAlpha014.readLine());
                for (int xaiAlpha015 = 1; xaiAlpha015 <= xaiAlpha010; ++xaiAlpha015) {
                    Scanner xaiAlpha011 = new Scanner(xaiAlpha014.readLine());
                    int xaiAlpha024 = xaiAlpha011.nextInt();
                    int xaiAlpha009 = xaiAlpha011.nextInt();
                    int xaiAlpha021 = xaiAlpha011.nextInt();
                    int xaiAlpha016 = xaiAlpha011.nextInt();
                    List<String> xaiAlpha012 = new ArrayList<>();
  /*                  char tmp[] = new char[(int)Math.pow(2, nn)];
                    Arrays.fill(tmp, 'P');
                    String tmpRes = null;
                    while (true) {
                        int cur = tmp.length - 1;
                        int r = rr;
                        int p = pp;
                        int s = ss;
                        boolean good = true;
                        for (char c: tmp) {
                            if ('P' == c)
                                --p;
                            if ('R' == c)
                                --r;
                            if ('S' == c)
                                --s;
                            if (p < 0 || s < 0 || r < 0) {
                                good = false;
                                break;
                            }
                        }
                        if (good) {
                            char tPrev[] = Arrays.copyOf(tmp, tmp.length);
                            while (tPrev.length > 1) {
                                char tCur[] = new char[tPrev.length / 2];
                                for(int i =0; i < tCur.length; ++i) {
                                    if ((tPrev[i*2] == 'R' && tPrev[i*2+1] == 'P')
                                        || (tPrev[i*2] == 'P' && tPrev[i*2+1] == 'R'))
                                        tCur[i] = 'P';
                                    else if ((tPrev[i*2] == 'R' && tPrev[i*2+1] == 'S')
                                            || (tPrev[i*2] == 'S' && tPrev[i*2+1] == 'R'))
                                        tCur[i] = 'R';
                                    else if ((tPrev[i*2] == 'P' && tPrev[i*2+1] == 'S')
                                            || (tPrev[i*2] == 'S' && tPrev[i*2+1] == 'P'))
                                        tCur[i] = 'S';
                                    else {
                                        good = false;
                                        break;
                                    }
                                }
                                tPrev = tCur;
                            }
                            if (good) {
                                String tt = new String(tmp);
                                if (tmpRes == null)
                                    tmpRes = tt;
                                else if (tmpRes.compareTo(tt) > 0)
                                    tmpRes = tt;
                            }
                        }

                        while( cur >= 0 && tmp[cur] == 'S')
                            --cur;
                        if (cur < 0)
                            break;
                        if (tmp[cur] == 'P')
                            tmp[cur] = 'R';
                        else if (tmp[cur] == 'R')
                            tmp[cur] = 'S';
                        for (int i = cur + 1; i < tmp.length; ++i)
                            tmp[i] = 'P';
                    }
                    if (tmpRes != null)
                        bw.write(tmpRes + "\n");
                    else
                        bw.write("IMPOSSIBLE" + "\n");
*/

                    xaiAlpha020:
                    for (int xaiAlpha020 = 0; xaiAlpha020 <= 2; ++xaiAlpha020) {
                        int xaiAlpha004 = xaiAlpha024;
                        int xaiAlpha007 = xaiAlpha009;
                        int xaiAlpha002 = xaiAlpha021;
                        int xaiAlpha000 = xaiAlpha016;
                        int xaiAlpha008 = 1;
                        char xaiAlpha013[] = new char[xaiAlpha008];
                        if (xaiAlpha020 == 0)
                            xaiAlpha013[0] = 'P';
                        if (xaiAlpha020 == 1)
                            xaiAlpha013[0] = 'R';
                        if (xaiAlpha020 == 2)
                            xaiAlpha013[0] = 'S';
                        int xaiAlpha025;
                        while (xaiAlpha004-- > 0) {
                            xaiAlpha025 = xaiAlpha008 * 2;
                            char xaiAlpha018[] = new char[xaiAlpha025];
                            for (int xaiAlpha022 = 0; xaiAlpha022 < xaiAlpha008; ++xaiAlpha022) {
                                if (xaiAlpha013[xaiAlpha022] == 'P') {
                                    xaiAlpha018[xaiAlpha022*2] = 'P';
                                    xaiAlpha018[xaiAlpha022*2 + 1] = 'R';
                                } else if (xaiAlpha013[xaiAlpha022] == 'R') {
                                    if (xaiAlpha004 == 0) {
                                        xaiAlpha018[xaiAlpha022*2] = 'R';
                                        xaiAlpha018[xaiAlpha022*2 + 1] = 'S';
                                    } else {
                                        xaiAlpha018[xaiAlpha022*2] = 'S';
                                        xaiAlpha018[xaiAlpha022*2 + 1] = 'R';
                                    }
                                } else if (xaiAlpha013[xaiAlpha022] == 'S') {
                                    if (xaiAlpha004 >= 2) {
                                        xaiAlpha018[xaiAlpha022*2] = 'S';
                                        xaiAlpha018[xaiAlpha022*2 + 1] = 'P';
                                    } else {
                                        xaiAlpha018[xaiAlpha022*2] = 'P';
                                        xaiAlpha018[xaiAlpha022*2 + 1] = 'S';
                                    }
                                }
                            }
                            xaiAlpha008 = xaiAlpha025;
                            xaiAlpha013 = xaiAlpha018;
                        }
                        int xaiAlpha019 = 1;
                        for (char xaiAlpha005: xaiAlpha013) {
                            if ('P' == xaiAlpha005)
                                --xaiAlpha002;
                            if ('R' == xaiAlpha005)
                                --xaiAlpha007;
                            if ('S' == xaiAlpha005)
                                --xaiAlpha000;
                            if (xaiAlpha002 < 0 || xaiAlpha000 < 0 || xaiAlpha007 < 0)
                                continue xaiAlpha020;
                        }
                        xaiAlpha012.add(new String(xaiAlpha013));
                    }
                    xaiAlpha017.write("Case #" + xaiAlpha015 + ": ");
                    if (xaiAlpha012.isEmpty())
                        xaiAlpha017.write("IMPOSSIBLE");
                    else {
                        String xaiAlpha023 = null;
                        for (String xaiAlpha000: xaiAlpha012) {
                            if (xaiAlpha023 == null)
                                xaiAlpha023 = xaiAlpha000;
                            else {
                                if (xaiAlpha023.compareTo(xaiAlpha000) > 0)
                                    xaiAlpha023 = xaiAlpha000;
                            }
                        }
                        xaiAlpha017.write(xaiAlpha023);
                    }
                    xaiAlpha017.write("\n");
                }
                xaiAlpha017.close();
            }

        } catch (IOException xaiAlpha006) {
            xaiAlpha006.printStackTrace();
        }
    }
}
