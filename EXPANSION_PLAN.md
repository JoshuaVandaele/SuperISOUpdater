# SuperISOUpdater Expansion Plan

## Phase 1: Infrastructure Enhancement (COMPLETED)

### New Base Classes Created

1. **GitHubReleaseUpdater** (`modules/updaters/base/GitHubReleaseUpdater.py`)
   - For projects that distribute via GitHub Releases
   - Automatically fetches latest release via GitHub API
   - Handles asset pattern matching
   - Extracts version from release tags
   
2. **DirectMirrorUpdater** (`modules/updaters/base/DirectMirrorUpdater.py`)
   - For projects with directory listing mirrors
   - Randomizes mirror selection for load distribution
   - Parses HTML directory listings
   - Finds latest version by filename pattern

### New Updaters Added

1. **Ventoy** - Bootable USB creation tool (GitHub Releases)
2. **Parrot Security OS** - Security/forensics distro
3. **MX Linux** - Popular Debian-based distro (SourceForge)
4. **Pop!_OS** - System76's Ubuntu variant (Intel & NVIDIA editions)
5. **Puppy Linux** - Lightweight, RAM-based distro (BionicPup variant)

## Phase 2: Next Wave of Updaters (TODO)

### Easy Additions (GitHub Releases):
- [ ] EndeavourOS - User-friendly Arch
- [ ] Porteus - Fast, portable Linux
- [ ] QubesOS - Security-focused OS
- [ ] Whonix - Privacy/anonymity OS

### Medium Complexity:
- [ ] Elementary OS - Beautiful desktop
- [ ] Zorin OS - Windows-like Linux
- [ ] pfSense - Firewall/router OS
- [ ] IPFire - Firewall distribution
- [ ] BlackArch - Penetration testing (large ISO)

### Complex (Requires Special Handling):
- [ ] VMware ESXi - Requires account/licensing
- [ ] XCP-ng - Citrix Hypervisor fork
- [ ] Harvester - Kubernetes HCI
- [ ] UnRAID - Requires license management

## Phase 3: Quality Improvements (TODO)

### Integrity Checking
- Implement SHA256 verification for all new updaters
- Add support for GPG signature verification
- Create helper functions for common checksum formats

### Error Handling
- Add retry logic with exponential backoff
- Better error messages for network failures
- Fallback mirror support

### Testing
- Unit tests for base classes
- Integration tests for updaters
- Mock HTTP responses for testing

## Usage

### Config File Example:
```toml
[Ventoy]
# Downloads latest Ventoy

[PopOS]
editions = ["intel", "nvidia"]
# Downloads both Intel/AMD and NVIDIA versions

[PuppyLinux]
# Downloads latest BionicPup

[ParrotSecurity]
# Downloads Parrot Security OS

[MXLinux]
# Downloads MX Linux
```

## Implementation Notes

### Benefits of New Structure:
1. **Reduced Code Duplication** - Base classes handle common patterns
2. **Easier Maintenance** - Fix once, apply to all
3. **Faster Development** - New updaters are simpler to write
4. **Consistent Behavior** - All updaters follow same patterns

### Migration Path:
Existing updaters can optionally be refactored to use base classes,
but this is not required. Old and new patterns coexist.

## Contributing New Updaters

### Using GitHubReleaseUpdater:
```python
from modules.updaters.base.GitHubReleaseUpdater import GitHubReleaseUpdater

class MyDistro(GitHubReleaseUpdater):
    github_repo = "owner/repo"
    asset_pattern = r"mydistro-.*\.iso$"
    
    def __init__(self, folder_path: Path):
        self.file_path = folder_path / "mydistro-[[VER]].iso"
        super().__init__(folder_path)
```

### Using DirectMirrorUpdater:
```python
from modules.updaters.base.DirectMirrorUpdater import DirectMirrorUpdater

class MyDistro(DirectMirrorUpdater):
    mirrors = ["https://mirror1.com/path/", "https://mirror2.com/path/"]
    iso_pattern = r"mydistro-\d+.*\.iso$"
    
    def __init__(self, folder_path: Path):
        self.file_path = folder_path / "mydistro-[[VER]].iso"
        super().__init__(folder_path)
```

## Next Steps

1. Test the new updaters with actual downloads
2. Implement checksum verification for each
3. Add more updaters using the base classes
4. Document the API for contributors
5. Create GitHub issue templates for new updater requests
