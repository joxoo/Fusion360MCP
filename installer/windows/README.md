# Windows Installer

This folder contains an Inno Setup definition for a user-friendly Windows installer:

- `FusionMCP.iss`

## Build

1. Install [Inno Setup](https://jrsoftware.org/isinfo.php).
2. Open `FusionMCP.iss` in the Inno Setup Compiler.
3. Build the installer.

The generated installer will be written to:

`installer/windows/output/FusionMCP-Setup-<version>.exe`

The version should come from `FusionMCP.manifest`.

## GitHub Actions

The repository also contains a Windows CI workflow:

- `.github/workflows/build-windows-installer.yml`
- `.github/workflows/release-windows-installer.yml`

It:

- runs on `windows-latest`
- installs Inno Setup
- reads the version from `FusionMCP.manifest`
- compiles `FusionMCP.iss`
- uploads the generated `Setup.exe` as a workflow artifact

You can trigger it manually with `workflow_dispatch` or let it run automatically on pushes to `main` that touch installer or shipped add-in files.

The release workflow additionally:

- runs on published GitHub releases
- runs on pushed tags matching `v*`
- attaches the generated installer directly to the GitHub release

## What it does

- Installs FusionMCP into:
  `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\FusionMCP`
- Avoids shipping development folders such as `__pycache__`
- Registers an uninstall entry

## Notes

- This installer does not bundle `uv`. The target machine still needs `uv` installed for the MCP process startup path used by the add-in.
- If you need a true `.msi`, the next step would be a WiX-based installer. The Inno Setup path is simpler to maintain and easier to ship first.
