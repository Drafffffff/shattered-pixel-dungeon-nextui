package org.nextui.shattered;
public final class SignalProbe {
 static final class Node { int value=7; }
 static volatile Node current;
 static int value(){return current.value;}
 public static void main(String[] args) {
  Sdl.init();
  try {
   Node node=new Node();int caught=0;
   for(int i=0;i<1000000;i++) {
    current=i%17==0?null:node;
    try{value();}catch(NullPointerException expected){caught++;}
   }
   if(caught!=58824)throw new AssertionError(caught);
   System.out.println("PASS: 58824 Java null checks after replacing all four JVM fault handlers during SDL init");
  } finally {Sdl.close();}
 }
}
