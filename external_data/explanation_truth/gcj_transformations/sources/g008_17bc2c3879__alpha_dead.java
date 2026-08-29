package googlejam3.p506;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

public class A {
	public static void main(String[] xaiAlpha000) throws NumberFormatException,
			IOException {
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

		try (BufferedReader xaiAlpha003 = new BufferedReader(new FileReader("input.txt"))) {
			int xaiAlpha007 = Integer.parseInt(xaiAlpha003.readLine());
			for (int xaiAlpha005 = 1; xaiAlpha005 <= xaiAlpha007; xaiAlpha005++) {
				String[] xaiAlpha001 = xaiAlpha003.readLine().split(" ");
				int xaiAlpha004 = Integer.parseInt(xaiAlpha001[0]);
				int xaiAlpha002 = Integer.parseInt(xaiAlpha001[1]);
				int xaiAlpha008 = Integer.parseInt(xaiAlpha001[2]);

				int xaiAlpha006 = 0;
				if (xaiAlpha002 == xaiAlpha008)
					xaiAlpha006 = xaiAlpha008;
				else {
					if (xaiAlpha002 % xaiAlpha008 == 0)
						xaiAlpha006 += xaiAlpha002 / xaiAlpha008 - 1;
					else
						xaiAlpha006 += xaiAlpha002 / xaiAlpha008;

					xaiAlpha006 += xaiAlpha008;
				}

				System.out.println("Case #" + xaiAlpha005 + ": " + xaiAlpha006);
			}
		}
	}
}
