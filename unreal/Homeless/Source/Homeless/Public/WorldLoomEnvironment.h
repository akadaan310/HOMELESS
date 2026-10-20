#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WorldLoomEnvironment.generated.h"
class UNiagaraComponent;
class UMaterialParameterCollection;
class UAudioComponent;
class USoundBase;
USTRUCT(BlueprintType)
struct FWorldLoomWeatherProjection {
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FVector ObservedWindMetersPerSecond=FVector::ZeroVector;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FVector AuthoredWindMetersPerSecond=FVector::ZeroVector;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float RainMillimetersPerHour=0;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float TemperatureCelsius=24;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FString SourceKind=TEXT("unknown");
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FString CellId;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FString EpochUTC;
};
UCLASS()
class HOMELESS_API AWorldLoomEnvironment : public AActor {
    GENERATED_BODY()
public:
    AWorldLoomEnvironment();
    virtual void Tick(float DeltaSeconds) override;
    UFUNCTION(BlueprintCallable) void ApplyWeather(const FWorldLoomWeatherProjection& Projection);
    UFUNCTION(BlueprintCallable) void ApplySound(float TrafficIntensity, float RecognitionEnvelope);
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FWorldLoomWeatherProjection Weather;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) TObjectPtr<UMaterialParameterCollection> SurfaceParameters;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UNiagaraComponent> Rain;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UAudioComponent> Ambience;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) TObjectPtr<USoundBase> MetaSoundProgram;
    UPROPERTY(BlueprintReadOnly) float Wetness=0;
private: float Traffic=0,Recognition=0;
};
