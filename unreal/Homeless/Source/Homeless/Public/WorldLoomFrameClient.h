#pragma once
// Shared by UE Linux adapter and standalone interoperability probe. Network I/O
// never runs on the Unreal game thread. This carries JSON only to the local
// presentation gateway; ACSP CBOR remains authoritative behind the gateway.
#include <string>
#include <cstdint>
#include <cstring>
#if defined(__linux__)
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <cerrno>
#endif
namespace worldloom {
inline constexpr std::uint32_t MaxFrame = 1024 * 1024;
inline bool Exchange(const std::string& path, const std::string& request,
                     std::string& response, std::string& error, int timeoutMs=2000) {
#if defined(__linux__)
    if (request.empty() || request.size()>MaxFrame) {error="invalid request frame size";return false;}
    sockaddr_un address{};address.sun_family=AF_UNIX;
    if(path.size()>=sizeof(address.sun_path)){error="Unix socket path too long";return false;}
    std::memcpy(address.sun_path,path.c_str(),path.size()+1);
    int fd=::socket(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0);
    if(fd<0){error="socket creation failed";return false;}
    timeval timeout{timeoutMs/1000,(timeoutMs%1000)*1000};
    ::setsockopt(fd,SOL_SOCKET,SO_RCVTIMEO,&timeout,sizeof(timeout));
    ::setsockopt(fd,SOL_SOCKET,SO_SNDTIMEO,&timeout,sizeof(timeout));
    auto fail=[&](const char* text){error=std::string(text)+": "+std::strerror(errno);::close(fd);return false;};
    if(::connect(fd,reinterpret_cast<sockaddr*>(&address),sizeof(address))!=0)return fail("gateway unavailable");
    auto sendAll=[&](const void* p,std::size_t n){auto b=static_cast<const char*>(p);while(n){auto k=::send(fd,b,n,MSG_NOSIGNAL);if(k<0&&errno==EINTR)continue;if(k<=0)return false;b+=k;n-=k;}return true;};
    auto recvAll=[&](void* p,std::size_t n){auto b=static_cast<char*>(p);while(n){auto k=::recv(fd,b,n,0);if(k<0&&errno==EINTR)continue;if(k<=0)return false;b+=k;n-=k;}return true;};
    std::uint32_t size=static_cast<std::uint32_t>(request.size());
    unsigned char header[4]={static_cast<unsigned char>(size>>24),static_cast<unsigned char>(size>>16),static_cast<unsigned char>(size>>8),static_cast<unsigned char>(size)};
    if(!sendAll(header,4)||!sendAll(request.data(),request.size()))return fail("gateway send failed");
    if(!recvAll(header,4))return fail("gateway response header failed");
    size=(std::uint32_t(header[0])<<24)|(std::uint32_t(header[1])<<16)|(std::uint32_t(header[2])<<8)|header[3];
    if(!size||size>MaxFrame){error="gateway response exceeds frame budget";::close(fd);return false;}
    response.resize(size);if(!recvAll(response.data(),size))return fail("gateway response truncated");
    ::close(fd);return true;
#else
    error="Unix IPC adapter requires Linux host; use separately authenticated transport adapter on other platforms";return false;
#endif
}
}
