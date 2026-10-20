using UnrealBuildTool;
public class Homeless : ModuleRules {
    public Homeless(ReadOnlyTargetRules Target) : base(Target) {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        CppStandard = CppStandardVersion.Cpp20;
        PublicDependencyModuleNames.AddRange(new string[]{"Core","CoreUObject","Engine","InputCore","Json","JsonUtilities","Niagara","PhysicsCore","AudioMixer"});
    }
}
