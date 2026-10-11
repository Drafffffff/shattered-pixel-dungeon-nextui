// SPDX-License-Identifier: GPL-3.0-or-later
package org.nextui.shattered;
final class Sdl {
 static { System.loadLibrary("shattered_sdl"); }
 static native void init();
 static native int[] poll();
 static native void swap();
 static native void close();
}
