#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <string>
#include <iostream>
#include <cstring>
std::string esc(const std::string&s){std::string o="\"";for(unsigned char c:s){if(c=='\\'||c=='\"')o+='\\';if(c<32){o+=' ';}else{o+=c;}}return o+"\"";}
int main(int argc,char**argv){
 bool curlmode=std::string(argv[0]).find("curl")!=std::string::npos;
 if(argc<2){std::cerr<<"darkctl time | query | propose <kind> <object> <text>\n";return 2;}
 std::string q="{\"command\":"+esc(curlmode?"curl":argv[1])+",\"args\":[";for(int i=curlmode?1:2;i<argc;i++){if(i>(curlmode?1:2))q+=",";q+=esc(argv[i]);}q+="]}";
 int fd=socket(AF_UNIX,SOCK_STREAM,0);sockaddr_un a{};a.sun_family=AF_UNIX;strcpy(a.sun_path,"/bus/control.sock");
 if(connect(fd,(sockaddr*)&a,sizeof(a))){std::cerr<<"IPC unavailable\n";return 3;}
 uint32_t n=htonl(q.size());if(write(fd,&n,4)!=4||write(fd,q.data(),q.size())!=(long)q.size())return 4;
 if(recv(fd,&n,4,MSG_WAITALL)!=4)return 4;n=ntohl(n);if(n>65536)return 5;std::string b(n,' ');if(recv(fd,b.data(),n,MSG_WAITALL)!=(long)n)return 4;
 std::cout<<b<<"\n";close(fd);return b.find("\"exit\":0")!=std::string::npos?0:1;
}
