#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "WorldLoomSubsystem.generated.h"

USTRUCT(BlueprintType)
struct FWorldLoomWorldProjection {
    GENERATED_BODY()
    UPROPERTY(BlueprintReadOnly) FString SessionId;
    UPROPERTY(BlueprintReadOnly) int64 Tick = 0;
    UPROPERTY(BlueprintReadOnly) double Latitude = 27.9596;
    UPROPERTY(BlueprintReadOnly) double Longitude = -82.5066;
    UPROPERTY(BlueprintReadOnly) FString SourceQuality = TEXT("unknown");
    UPROPERTY(BlueprintReadOnly) FString TraceDigest;
    UPROPERTY(BlueprintReadOnly) FString Json;
};
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FWorldLoomProjectionReady, const FWorldLoomWorldProjection&, Projection);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FWorldLoomTransportError, const FString&, Error);

UCLASS()
class HOMELESS_API UWorldLoomSubsystem : public UGameInstanceSubsystem {
    GENERATED_BODY()
public:
    UPROPERTY(BlueprintAssignable) FWorldLoomProjectionReady OnProjection;
    UPROPERTY(BlueprintAssignable) FWorldLoomTransportError OnTransportError;
    UPROPERTY(BlueprintReadOnly) FWorldLoomWorldProjection LatestProjection;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FString SocketPath = TEXT("/tmp/worldloom-unreal.sock");
    UFUNCTION(BlueprintCallable) bool RequestProjection(const FString& SessionId);
    UFUNCTION(BlueprintCallable) bool SubmitInput(const FString& SessionId, const FString& Operation, const FString& PayloadJson);
    virtual void Deinitialize() override;
private:
    bool bInFlight=false;
    bool bStopping=false;
    bool Send(const FString& RequestJson);
};
