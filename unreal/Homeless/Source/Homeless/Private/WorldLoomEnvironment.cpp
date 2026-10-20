#include "WorldLoomEnvironment.h"
#include "NiagaraComponent.h"
#include "Components/AudioComponent.h"
#include "Materials/MaterialParameterCollection.h"
#include "Materials/MaterialParameterCollectionInstance.h"
#include "Engine/World.h"
AWorldLoomEnvironment::AWorldLoomEnvironment() {
    PrimaryActorTick.bCanEverTick=true;RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    Rain=CreateDefaultSubobject<UNiagaraComponent>(TEXT("SourceRainFX"));Rain->SetupAttachment(RootComponent);Rain->SetAutoActivate(false);
    Ambience=CreateDefaultSubobject<UAudioComponent>(TEXT("SpatialMetaSound"));Ambience->SetupAttachment(RootComponent);Ambience->bAutoActivate=false;Ambience->bAllowSpatialization=true;
}
void AWorldLoomEnvironment::ApplyWeather(const FWorldLoomWeatherProjection& P) {
    Weather=P;
    Weather.RainMillimetersPerHour=FMath::Clamp(P.RainMillimetersPerHour,0.f,100.f);
    Weather.AuthoredWindMetersPerSecond=P.AuthoredWindMetersPerSecond.GetClampedToMaxSize(12);
    // Observed and authored channels stay distinct in the projection. No claim
    // that the gameplay perturbation is an actual meteorological hazard.
}
void AWorldLoomEnvironment::ApplySound(float T,float R){Traffic=FMath::Clamp(T,0.f,1.f);Recognition=FMath::Clamp(R,0.f,1.f);}
void AWorldLoomEnvironment::Tick(float Dt) {
    Super::Tick(Dt);const float H=FMath::Clamp(Dt,0.f,.05f);
    const float Evap=0.0008f*FMath::Max(0.f,Weather.TemperatureCelsius+5.f);
    Wetness=FMath::Clamp(Wetness+H*(Weather.RainMillimetersPerHour/120.f-Evap*Wetness-.01f*Wetness),0.f,1.f);
    const FVector Wind=Weather.ObservedWindMetersPerSecond+Weather.AuthoredWindMetersPerSecond;
    if(SurfaceParameters) {
        auto* Params=GetWorld()->GetParameterCollectionInstance(SurfaceParameters);
        Params->SetScalarParameterValue(TEXT("Wetness"),Wetness);
        Params->SetScalarParameterValue(TEXT("RainRate"),Weather.RainMillimetersPerHour);
        Params->SetVectorParameterValue(TEXT("WindMetersPerSecond"),FLinearColor(Wind.X,Wind.Y,Wind.Z,0));
    }
    Rain->SetVariableVec3(TEXT("User.WindVelocityCmPerSec"),Wind*100);
    Rain->SetVariableFloat(TEXT("User.RainRateMMPerHour"),Weather.RainMillimetersPerHour);
    if(Rain->GetAsset()){if(Weather.RainMillimetersPerHour>0&&!Rain->IsActive())Rain->Activate();else if(Weather.RainMillimetersPerHour<=0&&Rain->IsActive())Rain->Deactivate();}
    if(MetaSoundProgram&&Ambience->Sound!=MetaSoundProgram){Ambience->SetSound(MetaSoundProgram);Ambience->Play();}
    Ambience->SetFloatParameter(TEXT("Wetness"),Wetness);Ambience->SetFloatParameter(TEXT("WindSpeed"),Wind.Size());
    Ambience->SetFloatParameter(TEXT("TrafficIntensity"),Traffic);Ambience->SetFloatParameter(TEXT("RecognitionEnvelope"),Recognition);
}
