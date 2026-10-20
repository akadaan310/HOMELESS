#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "GameFramework/GameModeBase.h"
#include "HomelessPawn.generated.h"
class USpringArmComponent;
class UCameraComponent;

UENUM(BlueprintType)
enum class EWorldLoomCameraMode : uint8 {
    TrailingElevated, OverShoulder, CinemaArc, StreetEye, FirstPersonAR,
    FreeLook, VehicleInterior, VehicleFollow, DistantWitness, PortalTransition, BalloonAerial
};
UCLASS()
class HOMELESS_API AHomelessPawn : public ACharacter {
    GENERATED_BODY()
public:
    AHomelessPawn();
    virtual void Tick(float DeltaSeconds) override;
    virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
    UFUNCTION(BlueprintCallable) void SetCameraMode(EWorldLoomCameraMode NewMode, bool MotionReduced=false);
    UFUNCTION(BlueprintCallable) void SkipArrival();
    UPROPERTY(EditAnywhere, BlueprintReadWrite) EWorldLoomCameraMode CameraMode=EWorldLoomCameraMode::TrailingElevated;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) bool bMotionReduced=false;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<USpringArmComponent> CameraArm;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UCameraComponent> Camera;
private:
    void Forward(float Value);void Right(float Value);void Turn(float Value);void Look(float Value);void CycleCamera();
    FVector DesiredOffset=FVector(0,0,100);float DesiredLength=420;float DesiredPitch=-16;
    float ArrivalElapsed=0;bool bArrival=true;
};
UCLASS()
class HOMELESS_API AHomelessGameMode : public AGameModeBase {
    GENERATED_BODY()
public: AHomelessGameMode();
};
