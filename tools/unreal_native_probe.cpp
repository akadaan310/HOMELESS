#include "WorldLoomFrameClient.h"
#include <iostream>
int main(int argc,char** argv) {
    if(argc!=3){std::cerr<<"usage: unreal_native_probe SOCKET JSON_REQUEST\n";return 64;}
    std::string response,error;
    if(!worldloom::Exchange(argv[1],argv[2],response,error)){std::cerr<<error<<'\n';return 1;}
    std::cout<<response<<'\n';return 0;
}
