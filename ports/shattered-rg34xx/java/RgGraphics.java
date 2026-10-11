// SPDX-License-Identifier: GPL-3.0-or-later
package org.nextui.shattered;
import com.badlogic.gdx.Application;
import com.badlogic.gdx.graphics.GL20;
import com.badlogic.gdx.graphics.glutils.GLVersion;
import com.badlogic.gdx.backends.headless.mock.graphics.MockGraphics;
final class RgGraphics extends MockGraphics {
 private final GL20 gl;
 private final GLVersion version;
 RgGraphics(GL20 gl) { this.gl=gl; version=new GLVersion(Application.ApplicationType.Android,gl.glGetString(GL20.GL_VERSION),gl.glGetString(GL20.GL_VENDOR),gl.glGetString(GL20.GL_RENDERER)); }
 @Override public int getWidth(){return 720;}
 @Override public int getHeight(){return 480;}
 @Override public int getBackBufferWidth(){return 720;}
 @Override public int getBackBufferHeight(){return 480;}
 @Override public GL20 getGL20(){return gl;}
 @Override public GLVersion getGLVersion(){return version;}
 @Override public float getPpiX(){return 254;}
 @Override public float getPpiY(){return 254;}
 @Override public float getPpcX(){return 100;}
 @Override public float getPpcY(){return 100;}
 @Override public boolean isFullscreen(){return true;}
 @Override public boolean isContinuousRendering(){return true;}
 @Override public GraphicsType getType(){return GraphicsType.LWJGL3;}
 @Override public boolean supportsExtension(String s){return (" "+gl.glGetString(GL20.GL_EXTENSIONS)+" ").contains(" "+s+" ");}
 private static class Mode extends DisplayMode { Mode(){super(720,480,60,32);} }
 @Override public DisplayMode getDisplayMode(){return new Mode();}
}
