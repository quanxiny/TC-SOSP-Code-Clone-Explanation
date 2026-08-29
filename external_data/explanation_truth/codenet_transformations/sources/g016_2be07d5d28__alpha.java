import java.util.Scanner;
public class Main {
	public static void main(String[] xaiAlpha000){
		Scanner xaiAlpha007 = new Scanner(System.in);
        int xaiAlpha003 = xaiAlpha007.nextInt();
        int xaiAlpha006 = xaiAlpha007.nextInt();
        int xaiAlpha004 = xaiAlpha007.nextInt();
        int xaiAlpha002 = xaiAlpha007.nextInt();
        int xaiAlpha001 = xaiAlpha007.nextInt();
        int xaiAlpha005 = 0;
        if(xaiAlpha003+xaiAlpha006>2*xaiAlpha004){
            if(xaiAlpha002>=xaiAlpha001){
                if(xaiAlpha003>=2*xaiAlpha004){
                    xaiAlpha005 = 2*xaiAlpha004*xaiAlpha002;
                }else{
                    xaiAlpha005 = 2*xaiAlpha004*xaiAlpha001 + xaiAlpha003*(xaiAlpha002-xaiAlpha001);
                }
            }else{
                if(xaiAlpha006>=2*xaiAlpha004){
                    xaiAlpha005 = 2*xaiAlpha004*xaiAlpha001;
                }else{
                    xaiAlpha005 = 2*xaiAlpha004*xaiAlpha002 + xaiAlpha006*(xaiAlpha001-xaiAlpha002);
                }
            }
        }else{
            xaiAlpha005 = xaiAlpha003*xaiAlpha002+xaiAlpha006*xaiAlpha001;
        }
        
          System.out.println(xaiAlpha005);
        }
    }
