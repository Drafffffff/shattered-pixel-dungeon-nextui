/* SPDX-License-Identifier: GPL-3.0-or-later */
#include <jni.h>
#include <SDL.h>
#include <stdio.h>
#include <signal.h>
#include <linux/input.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
static SDL_Window *window;
static SDL_GLContext context;
static SDL_Joystick *joystick;
static int hat;
static int evdev_fd=-1,evdev_hat,input_log_count;
static int keycode(int code) {
 switch(code) {
 /* H700's firmware codes follow NextUI platform.h, not Linux's semantic
  * BTN_* names (for example code 310 is Select, not the Linux TL2 label). */
 case 304:return 96; case 305:return 97;
 case 307:return 99; case 306:return 100;
 case 308:return 102; case 309:return 103;
 case 310:return 109; case 311:return 108;
 case 312:return 106;
 case 314:return 104; case 315:return 105;
 case KEY_VOLUMEUP:return 20001; case KEY_VOLUMEDOWN:return 20002;
 case KEY_UP:return 1019; case KEY_DOWN:return 1020;
 case KEY_LEFT:return 1021; case KEY_RIGHT:return 1022;
 default:return 0;
 }
}
static void open_evdev(void) {
 /* H700 raw SDL indices vary between builds. Kernel codes are the same
  * codes NextUI uses and do not depend on PortMaster's controller DB. */
 const char *driver=SDL_GetCurrentVideoDriver();
 if(!driver || SDL_strcmp(driver,"mali")) return;
 for(int i=0;i<16;i++) {
  char path[64],name[128]={0};
  snprintf(path,sizeof(path),"/dev/input/event%d",i);
  int fd=open(path,O_RDONLY|O_NONBLOCK|O_CLOEXEC);
  if(fd<0) continue;
  if(ioctl(fd,EVIOCGNAME(sizeof(name)),name)>=0 && !SDL_strcmp(name,"ANBERNIC-keys")) {
   evdev_fd=fd;fprintf(stderr,"Input backend: evdev %s (%s), A=304 B=305\n",path,name);return;
  }
  close(fd);
 }
 fprintf(stderr,"Input backend: SDL fallback (ANBERNIC evdev unavailable)\n");
}
static void fail(JNIEnv *e) { (*e)->ThrowNew(e, (*e)->FindClass(e,"java/lang/IllegalStateException"), SDL_GetError()); }
JNIEXPORT void JNICALL Java_org_nextui_shattered_Sdl_init(JNIEnv *e,jclass c) {
 /* SDL's evdev console cleanup reraises faults, losing the original CPU
  * context HotSpot needs for implicit null checks and safepoints. Restore
  * the JVM handlers immediately after SDL initialization. */
 const int faults[]={SIGSEGV,SIGBUS,SIGILL,SIGFPE};
 struct sigaction jvm_handlers[4];
 for(int i=0;i<4;i++) if(sigaction(faults[i],NULL,&jvm_handlers[i])) {
  (*e)->ThrowNew(e,(*e)->FindClass(e,"java/lang/IllegalStateException"),"Cannot inspect JVM signal handlers"); return;
 }
 SDL_SetHint(SDL_HINT_NO_SIGNAL_HANDLERS,"1");
 SDL_SetHint(SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS,"1");
 int init_status=SDL_Init(SDL_INIT_VIDEO|SDL_INIT_JOYSTICK|SDL_INIT_EVENTS);
 int restored=0;
 for(int i=0;i<4;i++) {
  struct sigaction current;
  if(sigaction(faults[i],NULL,&current) || sigaction(faults[i],&jvm_handlers[i],NULL)) {
   (*e)->ThrowNew(e,(*e)->FindClass(e,"java/lang/IllegalStateException"),"Cannot restore JVM signal handlers"); return;
  }
  if(current.sa_sigaction!=jvm_handlers[i].sa_sigaction) restored++;
 }
 fprintf(stderr,"JVM signal handlers preserved (SDL replaced %d)\n",restored);
 if(init_status) { fail(e); return; }
 SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK,SDL_GL_CONTEXT_PROFILE_ES);
 SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION,2); SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION,0);
 SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER,1); SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE,0);
 window=SDL_CreateWindow("Shattered Pixel Dungeon",0,0,720,480,SDL_WINDOW_OPENGL|SDL_WINDOW_FULLSCREEN);
 if(!window) { fail(e); return; }
 context=SDL_GL_CreateContext(window); if(!context){ fail(e); return; }
 SDL_GL_SetSwapInterval(1); SDL_ShowCursor(SDL_DISABLE);
 fprintf(stderr,"SDL %s screen=%dx%d joysticks=%d\n",SDL_GetCurrentVideoDriver(),720,480,SDL_NumJoysticks());
 if(SDL_NumJoysticks()>0) { joystick=SDL_JoystickOpen(0); fprintf(stderr,"Input: %s buttons=%d hats=%d axes=%d\n",SDL_JoystickName(joystick),SDL_JoystickNumButtons(joystick),SDL_JoystickNumHats(joystick),SDL_JoystickNumAxes(joystick)); }
 open_evdev();
}
/* libGDX controller key codes. RG34XX shares the H700 ANBERNIC mapping. */
static int button(int b) { switch(b) {
 case 4:return 96; case 3:return 97; case 6:return 99; case 5:return 100;
 case 7:return 102; case 8:return 103; case 9:return 109; case 10:return 108;
 case 11:return 106; case 12:return 104; case 13:return 105; default:return 0;
} }
JNIEXPORT jintArray JNICALL Java_org_nextui_shattered_Sdl_poll(JNIEnv *e,jclass c) {
 SDL_Event ev; jint keys[256]; int n=0;
 if(evdev_fd>=0) {
  struct input_event input;
  while(n<240 && read(evdev_fd,&input,sizeof(input))==sizeof(input)) {
   if(input.type==EV_KEY && input.value!=2) {
    int k=keycode(input.code);
    if(k) {keys[n++]=input.value?k:-k;
     if(input_log_count++<80) fprintf(stderr,"Input kernel=%u value=%d game=%d\n",input.code,input.value,keys[n-1]);
    }
   } else if(input.type==EV_ABS && (input.code==ABS_HAT0X || input.code==ABS_HAT0Y)) {
    int before=evdev_hat;
    if(input.code==ABS_HAT0X) evdev_hat=(evdev_hat&~10)|(input.value<0?8:input.value>0?2:0);
    else evdev_hat=(evdev_hat&~5)|(input.value<0?1:input.value>0?4:0);
    int bits[]={1,4,8,2},codes[]={1019,1020,1021,1022};
    for(int i=0;i<4;i++) if((before&bits[i])!=(evdev_hat&bits[i])) {
     keys[n++]=(evdev_hat&bits[i])?codes[i]:-codes[i];
     if(input_log_count++<80) fprintf(stderr,"Input hat=%d game=%d\n",evdev_hat,keys[n-1]);
    }
   }
  }
 }
 while(n<248 && SDL_PollEvent(&ev)) {
 if(ev.type==SDL_QUIT) keys[n++]=99999;
 else if(evdev_fd<0 && (ev.type==SDL_JOYBUTTONDOWN||ev.type==SDL_JOYBUTTONUP)) { int k=button(ev.jbutton.button); if(k) keys[n++]=ev.type==SDL_JOYBUTTONDOWN?k:-k; }
 else if(evdev_fd<0 && ev.type==SDL_JOYHATMOTION) { int bits[]={1,4,8,2},codes[]={1019,1020,1021,1022}; for(int i=0;i<4;i++) if((hat&bits[i])!=(ev.jhat.value&bits[i])) keys[n++]=(ev.jhat.value&bits[i])?codes[i]:-codes[i]; hat=ev.jhat.value; }
 }
 jintArray a=(*e)->NewIntArray(e,n); (*e)->SetIntArrayRegion(e,a,0,n,keys); return a;
}
JNIEXPORT void JNICALL Java_org_nextui_shattered_Sdl_swap(JNIEnv *e,jclass c) { SDL_GL_SwapWindow(window); }
JNIEXPORT void JNICALL Java_org_nextui_shattered_Sdl_close(JNIEnv *e,jclass c) { if(evdev_fd>=0) {close(evdev_fd);evdev_fd=-1;} if(joystick) SDL_JoystickClose(joystick); if(context)SDL_GL_DeleteContext(context); if(window)SDL_DestroyWindow(window); SDL_Quit(); }
