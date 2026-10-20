#include "WorldLoomSubsystem.h"
#include "WorldLoomFrameClient.h"
#include "Async/Async.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

static FString Encode(const TSharedRef<FJsonObject>& Object) {
    FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(Object,Writer);return Text;
}
bool UWorldLoomSubsystem::RequestProjection(const FString& SessionId) {
    auto Request=MakeShared<FJsonObject>();Request->SetStringField(TEXT("protocol"),TEXT("worldloom.unreal.v1"));
    Request->SetStringField(TEXT("request_id"),FGuid::NewGuid().ToString(EGuidFormats::DigitsWithHyphens));
    Request->SetStringField(TEXT("operation"),TEXT("projection"));Request->SetStringField(TEXT("session_id"),SessionId);
    return Send(Encode(Request));
}
bool UWorldLoomSubsystem::SubmitInput(const FString& SessionId,const FString& Operation,const FString& PayloadJson) {
    TSharedPtr<FJsonObject> Payload;
    if(!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(PayloadJson),Payload)||!Payload.IsValid())return false;
    auto Request=MakeShared<FJsonObject>();Request->SetStringField(TEXT("protocol"),TEXT("worldloom.unreal.v1"));
    Request->SetStringField(TEXT("request_id"),FGuid::NewGuid().ToString(EGuidFormats::DigitsWithHyphens));
    Request->SetStringField(TEXT("operation"),Operation);Request->SetStringField(TEXT("session_id"),SessionId);Request->SetObjectField(TEXT("payload"),Payload);
    return Send(Encode(Request));
}
bool UWorldLoomSubsystem::Send(const FString& RequestJson) {
    if(bStopping||bInFlight)return false;bInFlight=true;
    const auto Path=std::string(TCHAR_TO_UTF8(*SocketPath));const auto Request=std::string(TCHAR_TO_UTF8(*RequestJson));
    const TWeakObjectPtr<UWorldLoomSubsystem> WeakThis(this);
    Async(EAsyncExecution::ThreadPool,[WeakThis,Path,Request]() {
        std::string Response,Error;const bool Ok=worldloom::Exchange(Path,Request,Response,Error);
        const FString Reply=UTF8_TO_TCHAR(Response.c_str());const FString Failure=UTF8_TO_TCHAR(Error.c_str());
        AsyncTask(ENamedThreads::GameThread,[WeakThis,Ok,Reply,Failure]() {
            if(!WeakThis.IsValid()||WeakThis->bStopping)return;
            auto* Self=WeakThis.Get();Self->bInFlight=false;
            if(!Ok){Self->OnTransportError.Broadcast(Failure);return;}
            TSharedPtr<FJsonObject> Object;
            if(!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Reply),Object)||!Object.IsValid()){Self->OnTransportError.Broadcast(TEXT("Malformed gateway JSON"));return;}
            FString Status;Object->TryGetStringField(TEXT("status"),Status);
            if(Status!=TEXT("ok")){Self->OnTransportError.Broadcast(Reply);return;}
            FWorldLoomWorldProjection Projection;Projection.Json=Reply;Object->TryGetStringField(TEXT("trace_digest"),Projection.TraceDigest);
            const TSharedPtr<FJsonObject>* Data=nullptr;
            if(Object->TryGetObjectField(TEXT("data"),Data)) {
                (*Data)->TryGetStringField(TEXT("session_id"),Projection.SessionId);
                double Tick=0;(*Data)->TryGetNumberField(TEXT("tick"),Tick);Projection.Tick=static_cast<int64>(Tick);
                (*Data)->TryGetNumberField(TEXT("latitude"),Projection.Latitude);(*Data)->TryGetNumberField(TEXT("longitude"),Projection.Longitude);
                (*Data)->TryGetStringField(TEXT("source_quality"),Projection.SourceQuality);
            }
            const TSharedPtr<FJsonObject>* Presentation=nullptr;
            if(Object->TryGetObjectField(TEXT("presentation"),Presentation)) {
                (*Presentation)->TryGetStringField(TEXT("session_id"),Projection.SessionId);
                double Tick=0;(*Presentation)->TryGetNumberField(TEXT("tick"),Tick);Projection.Tick=static_cast<int64>(Tick);
                (*Presentation)->TryGetNumberField(TEXT("latitude"),Projection.Latitude);(*Presentation)->TryGetNumberField(TEXT("longitude"),Projection.Longitude);
                (*Presentation)->TryGetStringField(TEXT("source_quality"),Projection.SourceQuality);
            }
            Self->LatestProjection=Projection;Self->OnProjection.Broadcast(Projection);
        });
    });return true;
}
void UWorldLoomSubsystem::Deinitialize(){bStopping=true;Super::Deinitialize();}
