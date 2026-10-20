#include "HomelessPawn.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Components/InputComponent.h"
#include "Components/CapsuleComponent.h"

AHomelessGameMode::AHomelessGameMode(){DefaultPawnClass=AHomelessPawn::StaticClass();}
AHomelessPawn::AHomelessPawn() {
    PrimaryActorTick.bCanEverTick=true;GetCapsuleComponent()->InitCapsuleSize(34,88);
    GetCharacterMovement()->MaxWalkSpeed=160;GetCharacterMovement()->bOrientRotationToMovement=true;
    bUseControllerRotationYaw=false;
    CameraArm=CreateDefaultSubobject<USpringArmComponent>(TEXT("ComfortCameraArm"));CameraArm->SetupAttachment(RootComponent);
    CameraArm->TargetArmLength=420;CameraArm->SocketOffset=FVector(0,0,100);CameraArm->bUsePawnControlRotation=true;
    CameraArm->bDoCollisionTest=true;CameraArm->ProbeSize=14;CameraArm->bEnableCameraLag=true;CameraArm->CameraLagSpeed=8;
    CameraArm->bUseCameraLagSubstepping=true;CameraArm->CameraLagMaxTimeStep=1.f/120.f;
    Camera=CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));Camera->SetupAttachment(CameraArm,USpringArmComponent::SocketName);Camera->FieldOfView=65;
    // No placeholder mannequin/cubes. Assign an imported, licensed skeletal mesh.
}
void AHomelessPawn::SetupPlayerInputComponent(UInputComponent* Input) {
    Super::SetupPlayerInputComponent(Input);
    Input->BindAxis(TEXT("MoveForward"),this,&AHomelessPawn::Forward);Input->BindAxis(TEXT("MoveRight"),this,&AHomelessPawn::Right);
    Input->BindAxis(TEXT("Turn"),this,&AHomelessPawn::Turn);Input->BindAxis(TEXT("LookUp"),this,&AHomelessPawn::Look);
    Input->BindAction(TEXT("CycleCamera"),IE_Pressed,this,&AHomelessPawn::CycleCamera);
}
void AHomelessPawn::Forward(float V){if(Controller&&V!=0){SkipArrival();const FRotator Yaw(0,Controller->GetControlRotation().Yaw,0);AddMovementInput(FRotationMatrix(Yaw).GetUnitAxis(EAxis::X),V);}}
void AHomelessPawn::Right(float V){if(Controller&&V!=0){SkipArrival();const FRotator Yaw(0,Controller->GetControlRotation().Yaw,0);AddMovementInput(FRotationMatrix(Yaw).GetUnitAxis(EAxis::Y),V);}}
void AHomelessPawn::Turn(float V){AddControllerYawInput(FMath::Clamp(V,-8.f,8.f)*(bMotionReduced?.55f:1.f));}
void AHomelessPawn::Look(float V){if(Controller){auto R=Controller->GetControlRotation();R.Pitch=FMath::ClampAngle(R.Pitch+V,-65,35);R.Roll=0;Controller->SetControlRotation(R);}}
void AHomelessPawn::CycleCamera(){SetCameraMode(static_cast<EWorldLoomCameraMode>((static_cast<int>(CameraMode)+1)%11),bMotionReduced);}
void AHomelessPawn::SkipArrival(){bArrival=false;SetCameraMode(EWorldLoomCameraMode::TrailingElevated,bMotionReduced);}
void AHomelessPawn::SetCameraMode(EWorldLoomCameraMode Mode,bool Reduced) {
    CameraMode=Mode;bMotionReduced=Reduced;DesiredOffset=FVector(0,0,100);DesiredLength=420;DesiredPitch=-16;
    switch(Mode) {
    case EWorldLoomCameraMode::OverShoulder:DesiredOffset=FVector(0,55,75);DesiredLength=230;DesiredPitch=-8;break;
    case EWorldLoomCameraMode::FirstPersonAR:case EWorldLoomCameraMode::StreetEye:DesiredLength=0;DesiredOffset=FVector(0,0,65);DesiredPitch=0;break;
    case EWorldLoomCameraMode::CinemaArc:DesiredLength=700;DesiredPitch=-25;break;
    case EWorldLoomCameraMode::FreeLook:DesiredLength=600;DesiredPitch=-20;break;
    case EWorldLoomCameraMode::VehicleInterior:DesiredLength=0;DesiredOffset=FVector(25,-30,60);DesiredPitch=0;break;
    case EWorldLoomCameraMode::VehicleFollow:DesiredLength=700;DesiredOffset=FVector(0,0,130);DesiredPitch=-12;break;
    case EWorldLoomCameraMode::DistantWitness:DesiredLength=1600;DesiredPitch=-35;break;
    case EWorldLoomCameraMode::PortalTransition:DesiredLength=900;DesiredPitch=-20;break;
    case EWorldLoomCameraMode::BalloonAerial:DesiredLength=2400;DesiredPitch=-55;break;
    default:break;
    }
    if(Controller){auto R=Controller->GetControlRotation();R.Pitch=DesiredPitch;R.Roll=0;Controller->SetControlRotation(R);}
}
void AHomelessPawn::Tick(float Dt) {
    Super::Tick(Dt);
    const float Step=FMath::Clamp(Dt,0.f,0.05f);
    if(bArrival&&!bMotionReduced){ArrivalElapsed+=Step;const float T=FMath::Clamp(ArrivalElapsed/8.f,0.f,1.f);const float S=T*T*T*(10.f+T*(-15.f+6.f*T));DesiredLength=FMath::Lerp(2400.f,420.f,S);if(T>=1)bArrival=false;}
    // Exponential convergence is time-step invariant for constant targets;
    // collision recovery uses SpringArm's swept, substepped camera controller.
    const float Alpha=1.f-FMath::Exp(-6.f*Step);
    CameraArm->TargetArmLength=FMath::Lerp(CameraArm->TargetArmLength,DesiredLength,Alpha);
    CameraArm->SocketOffset=FMath::Lerp(CameraArm->SocketOffset,DesiredOffset,Alpha);
}
