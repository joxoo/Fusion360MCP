#define MyAppName "FusionMCP"
#ifndef MyAppVersion
  #define MyAppVersion "0.0.0-dev"
#endif
#define MyAppPublisher "Joxoo Software Solution"
#define MyAppURL "https://github.com/"
#define MyAppExeName "FusionMCP.py"

[Setup]
AppId={{B6A4A15B-568E-4A6C-9C7A-568E4A6C9C7A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={userappdata}\Autodesk\Autodesk Fusion 360\API\AddIns\FusionMCP
DisableDirPage=yes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=output
OutputBaseFilename=FusionMCP-Setup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\FusionMCP.manifest
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "startfusion"; Description: "Show a reminder to start Fusion 360 after installation"; Flags: unchecked

[Files]
Source: "..\..\FusionMCP.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\FusionMCP.manifest"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\fusion_mcp_server.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\CHANGELOG.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\core\*"; DestDir: "{app}\core"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__\*"
Source: "..\..\modules\*"; DestDir: "{app}\modules"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__\*"
Source: "..\..\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__\*"
Source: "..\..\scripts\generate_ai_usage.py"; DestDir: "{app}\scripts"; Flags: ignoreversion

[Dirs]
Name: "{app}\scripts"

[UninstallDelete]
Type: filesandordirs; Name: "{app}\core\__pycache__"
Type: filesandordirs; Name: "{app}\modules\__pycache__"
Type: filesandordirs; Name: "{app}\docs\__pycache__"
Type: filesandordirs; Name: "{app}\scripts\__pycache__"

[Run]
Filename: "{cmd}"; Parameters: "/C echo FusionMCP installed in {app}"; Flags: runhidden skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox(
      'FusionMCP was installed into the Fusion 360 Add-Ins folder.' + #13#10 + #13#10 +
      'Next steps:' + #13#10 +
      '1. Ensure uv is installed on this machine.' + #13#10 +
      '2. Start Fusion 360.' + #13#10 +
      '3. Open Utilities > Scripts and Add-Ins.' + #13#10 +
      '4. Start the FusionMCP add-in.',
      mbInformation,
      MB_OK
    );
  end;
end;
