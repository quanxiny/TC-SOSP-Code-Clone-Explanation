import java.util.*;
public class Main {
	public static void main(String[] xaiAlpha000){
        int __xai_dead_000 = 0;
        if (__xai_dead_000 != 0) { System.out.print(""); }

		Scanner xaiAlpha010 = new Scanner(System.in);
		// 整数の入力
		String xaiAlpha008[] = xaiAlpha010.next().split("");
        List<String> xaiAlpha005 = new ArrayList<>();
        for(int xaiAlpha009 = 0;xaiAlpha009 < xaiAlpha008.length;xaiAlpha009++){
         xaiAlpha005.add(xaiAlpha008[xaiAlpha009]);
        }
      
        String xaiAlpha003[] = xaiAlpha010.next().split("");
        List<String> xaiAlpha006 = new ArrayList<>();
        for(int xaiAlpha009 = 0;xaiAlpha009 < xaiAlpha003.length;xaiAlpha009++){
         xaiAlpha006.add(xaiAlpha003[xaiAlpha009]);
        }
        String xaiAlpha002[] = xaiAlpha010.next().split("");
        List<String> xaiAlpha007 = new ArrayList<>();
        for(int xaiAlpha009 = 0;xaiAlpha009 < xaiAlpha002.length;xaiAlpha009++){
         xaiAlpha007.add(xaiAlpha002[xaiAlpha009]);
        }
      
      
        String xaiAlpha001 = "a";
      
       try{
          while(true){
          if(xaiAlpha001.equals("a")){
            xaiAlpha001 = (String)xaiAlpha005.get(0);
            xaiAlpha005.remove(0);
          }else if(xaiAlpha001.equals("b")){
            xaiAlpha001 = (String)xaiAlpha006.get(0);
            xaiAlpha006.remove(0);
          }else if(xaiAlpha001.equals("c")){
            xaiAlpha001 = (String)xaiAlpha007.get(0);
            xaiAlpha007.remove(0);
          }
          }
        }catch(Exception xaiAlpha004){
          
          System.out.println(xaiAlpha001.toUpperCase());
        }
        
      
    }
}