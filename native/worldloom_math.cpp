// HOMELESS bounded numerical kernel. C ABI is shared by Python and runtime adapters.
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
#include <string>

extern "C" {
// 0 certified, 1 infeasible, 2 unsupported, 3 unbounded, 4 budget.
int wl_box_qp(int n, const double* h, const double* g, const double* lo,
              const double* hi, double* out) {
    if(n < 1 || n > 256) return 4;
    for(int i=0; i<n; ++i) {
        if(lo[i] > hi[i]) return 1;
        if(!std::isfinite(h[i]) || !std::isfinite(g[i]) || h[i] < 0) return 2;
        double x = h[i] > 0 ? -g[i]/h[i] : 0;
        if(h[i] == 0 && g[i] > 0) x=lo[i];
        if(h[i] == 0 && g[i] < 0) x=hi[i];
        if(!std::isfinite(x)) return 3;
        out[i]=std::clamp(x,lo[i],hi[i]);
    }
    return 0;
}
int wl_decay(double rate, double initial, double duration, int steps, double* out) {
    if(steps < 1 || steps > 100000) return 4;
    if(rate < 0 || duration < 0 || !std::isfinite(initial) || rate*duration/steps > 1) return 2;
    double y=initial, dt=duration/steps;
    for(int i=0;i<steps;++i) {
        double k1=-rate*y, k2=-rate*(y+dt*k1/2), k3=-rate*(y+dt*k2/2), k4=-rate*(y+dt*k3);
        y+=dt*(k1+2*k2+2*k3+k4)/6;
    }
    *out=y; return 0;
}
int wl_game(int rows,int cols,const double* a,const double* b,int* equilibria) {
    if(rows<1 || cols<1 || rows>8 || cols>8) return -1;
    int count=0;
    for(int r=0;r<rows;++r) for(int c=0;c<cols;++c) {
        bool stable=true;
        for(int k=0;k<rows;++k) if(a[k*cols+c]>a[r*cols+c]+1e-12) stable=false;
        for(int k=0;k<cols;++k) if(b[r*cols+k]>b[r*cols+c]+1e-12) stable=false;
        if(stable) equilibria[count++]=r*cols+c;
    }
    return count;
}
// Fixed 720 Hz controller lattice, integrated once, sampled by each render profile.
int wl_camera(double duration,double* out,int capacity) {
    int n=int(std::llround(duration*720))+1;
    if(n<2 || n>capacity || n>43201) return -1;
    double x=0,v=0,a=0,dt=1.0/720;
    for(int i=0;i<n;++i) {
        double t=i*dt, target=4*std::sin(1.3*t)+1.2*std::sin(6*t);
        if(i) {
            double desired=std::clamp(16*(target-x)-8*v,-6.0,6.0);
            a+=std::clamp(desired-a,-25*dt,25*dt);
            v=std::clamp(v+a*dt,-10.0,10.0); x+=v*dt;
            if(x < -20 || x > 20) { x=std::clamp(x,-20.0,20.0); v=0; a=0; }
        }
        out[5*i]=t; out[5*i+1]=x; out[5*i+2]=v; out[5*i+3]=a; out[5*i+4]=target;
    }
    return n;
}
void wl_weather(double x,double y,double t,double radius,double* out) {
    double q=(x*x+y*y)/(radius*radius),amp=3*radius/1.7173002067198384*std::sin(.8*t);
    double s=std::max(0.0,1-q), k=6*amp/(radius*radius)*s*s;
    out[0]=2-k*y; out[1]=k*x; out[2]=0;
    out[3]= q<1 ? 12*amp/(radius*radius)*(1-q)*(1-3*q) : 0;
}
}
#ifndef WORLDLOOM_LIBRARY
int main(int argc,char** argv) {
    std::cout << std::setprecision(17);
    if(argc==2 && std::string(argv[1])=="self-test") {
        double h[]={2,4},g[]={-6,8},lo[]={0,-1},hi[]={2,3},x[2],y;
        int s=wl_box_qp(2,h,g,lo,hi,x); wl_decay(.7,3,4,400,&y);
        std::cout << "{\"solver\":\"worldloom-native-1\",\"status\":"<<s<<",\"qp\":["<<x[0]<<","<<x[1]<<"],\"ode\":"<<y<<"}\n";
        return s;
    }
    std::cerr << "Usage: worldloom-math self-test\n"; return 64;
}
#endif
