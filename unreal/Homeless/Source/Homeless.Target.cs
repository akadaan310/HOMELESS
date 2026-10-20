using UnrealBuildTool;
using System.Collections.Generic;
public class HomelessTarget : TargetRules {
    public HomelessTarget(TargetInfo Target) : base(Target) {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("Homeless");
    }
}
