#include <SDL.h>
#include <signal.h>
#include <unistd.h>
extern int __real_SDL_Init(Uint32 flags);
static void lost_jvm_context(int s) { _exit(90+s); }
int __wrap_SDL_Init(Uint32 flags) {
 int r=__real_SDL_Init(flags);
 const int faults[]={SIGSEGV,SIGBUS,SIGILL,SIGFPE};
 struct sigaction a={0};a.sa_handler=lost_jvm_context;sigemptyset(&a.sa_mask);
 for(int i=0;i<4;i++) sigaction(faults[i],&a,0);
 return r;
}
