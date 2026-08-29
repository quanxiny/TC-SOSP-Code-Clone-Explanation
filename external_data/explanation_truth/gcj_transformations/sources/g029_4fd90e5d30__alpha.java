package googlejam6.p418;
import java.io.File;
import java.io.IOException;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.util.HashSet;
import java.util.ArrayList;
import java.util.*;
import java.lang.StringBuilder;
import java.lang.Math;
class MyClass 
{



public static void main(String[] xaiAlpha009) throws Exception
{
BufferedReader xaiAlpha006=new BufferedReader(new FileReader(new File("C:\\Java\\A-small-attempt0.in")));
BufferedWriter xaiAlpha008=new BufferedWriter(new FileWriter(new File("C:\\Java\\A-large.out")));
BufferedWriter xaiAlpha000=new BufferedWriter(new FileWriter(new File("C:\\Java\\PractiseData2.out")));	

int xaiAlpha013 = java.lang.Integer.parseInt(xaiAlpha006.readLine());
String[] xaiAlpha010;
int[] xaiAlpha004 = new int[2501];
for(int xaiAlpha012=0;xaiAlpha012<xaiAlpha013;++xaiAlpha012)
{

//initialize zero
for(int xaiAlpha001=0;xaiAlpha001<2501;xaiAlpha001++)
{
xaiAlpha004[xaiAlpha001]=0;
}

int xaiAlpha007 = java.lang.Integer.parseInt(xaiAlpha006.readLine());
	for(int xaiAlpha002=0;xaiAlpha002<(xaiAlpha007*2-1);++xaiAlpha002)
	{
		xaiAlpha010=xaiAlpha006.readLine().split(" ");
		for(int xaiAlpha011=0;xaiAlpha011<xaiAlpha007;xaiAlpha011++)
		{
		xaiAlpha004[java.lang.Integer.parseInt(xaiAlpha010[xaiAlpha011])]++;
		}
	}


xaiAlpha008.write("Case #"+(xaiAlpha012+1)+": ");
int xaiAlpha003=1;
for(int xaiAlpha005=0;xaiAlpha005<2501;xaiAlpha005++)
{
if(xaiAlpha004[xaiAlpha005]>0)
xaiAlpha000.write(""+xaiAlpha005+"="+xaiAlpha004[xaiAlpha005]+" ");
if(xaiAlpha004[xaiAlpha005]>0)
{
if(xaiAlpha004[xaiAlpha005]%2!=0)
{
if(xaiAlpha003 == xaiAlpha007)
xaiAlpha008.write(""+(xaiAlpha005));
else
xaiAlpha008.write(""+(xaiAlpha005)+" ");
xaiAlpha003++;
}
}
}

xaiAlpha008.newLine();

}
xaiAlpha008.close();
xaiAlpha000.close();
}
}


