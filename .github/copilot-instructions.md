# MicroStack / Snap-OpenStack AI Coding Agent Instructions

## Project Overview

MicroStack is a snap-based OpenStack deployment solution leveraging Kubernetes, Juju charms, and MicroCluster for simplified cloud management. The codebase consists of three primary components:

1. **sunbeam-python/** - Python CLI (`sunbeam`) and orchestration logic
2. **sunbeam-microcluster/** - Go-based cluster daemon (`clusterd`) using dqlite for distributed state
3. **snap/** - Snapcraft packaging that bundles everything into a single snap

## Architecture Patterns

### Step-Based Execution Model

All operations are implemented as **Steps** (subclasses of `BaseStep` from `sunbeam/core/common.py`). Steps follow a consistent pattern:

```python
class MyStep(BaseStep):
    def __init__(self, ...):
        super().__init__("Step Name", "Step description")
    
    def prompt(self, console: Console | None = None, show_hint: bool = False) -> None:
        """Gather user input before execution"""
        # Use QuestionBank from sunbeam.core.questions
        pass
    
    def has_prompts(self) -> bool:
        """Return True if step needs user interaction"""
        return True
    
    def is_skip(self, status: Status | None = None) -> Result:
        """Determine if step should be skipped"""
        return Result(ResultType.COMPLETED)
    
    def run(self, status: Status | None = None) -> Result:
        """Execute the step logic"""
        try:
            # Do work
            return Result(ResultType.COMPLETED)
        except Exception as e:
            return Result(ResultType.FAILED, str(e))
```

**Key Step Patterns:**
- Steps in `sunbeam/provider/local/steps.py` handle local deployment specifics (NICs, SR-IOV, DPDK)
- Steps extend base implementations (e.g., `LocalSetHypervisorUnitsOptionsStep` extends `SetHypervisorUnitsOptionsStep`)
- Interactive prompts use `sunbeam.core.questions.QuestionBank` for validation and defaults
- All hardware introspection happens via Juju actions on `openstack-hypervisor` charm (see `nic_utils.fetch_nics()`)

### Juju Integration

Juju is the primary orchestration layer. Key helpers:

- **JujuHelper** (`sunbeam/core/juju.py`): Wraps `juju` CLI operations
  - `run_action()`: Execute Juju actions on units
  - `get_leader_unit()`: Find leader unit of an application
  - `wait_application_ready()`: Wait for application to reach desired state
  
- Always use JujuHelper instead of raw subprocess calls for Juju operations
- Models follow pattern: `{deployment.name}/{model_name}` (e.g., `sunbeam/openstack-machines`)

### Clusterd Integration

The MicroCluster daemon (`sunbeam-microcluster/`) provides distributed state storage:

- **Client** (`sunbeam/clusterd/client.py`): Python client for clusterd REST API
- Use `client.cluster.get_config(key)` / `set_config(key, value)` for persistent config
- Node membership tracked through `client.cluster.list_nodes_by_role(role)`
- Answers to interactive prompts stored via `sunbeam.core.questions.load_answers()` / `write_answers()`

### Manifest System

Manifests define software versions and configuration (`manifests/` directory):

```yaml
core:
  software:
    charms:
      glance-k8s:
        channel: 2024.1/beta  # Charm channel
        revision: 123          # Optional pinned revision
        config:
          snap-channel: 2024.1/beta
features:
  dns:
    software:
      charms:
        designate-k8s:
          channel: 2024.1/beta
```

- Manifests are pydantic models (`sunbeam/core/manifest.py`)
- User manifests merge over embedded defaults
- Version detection uses `infer_version()` and `infer_risk()` from snap channels

## Development Workflows

### Building the Snap

```bash
# Install dependencies
sudo snap install snapcraft --classic
sudo snap install --channel 1.21 --classic go

# Build snap
snapcraft
# Produces: openstack_2024.1_amd64.snap
```

### Testing Changes

**Unit tests:**
```bash
cd sunbeam-python/
tox -e unit
```

**Functional tests** (require hardware - see `sunbeam-python/tests/README.md`):
```bash
tox -e functional -- --sriov-interface-name=eno2 --manifest-path ~/manifest.yaml
```

**Code quality:**
```bash
tox -e pep8   # Ruff linting/formatting
tox -e mypy   # Type checking
tools/fast8.sh  # Quick check on modified files only
```

### Deploying Local Snap

See `docs/deploy-locally-built-snap.md`:

```bash
sudo snap install --dangerous openstack_*.snap
sudo snap alias openstack.sunbeam sunbeam
sunbeam prepare-node-script --bootstrap | bash -x
sudo snap connect openstack:juju-bin juju:juju-bin
# ... (see doc for complete steps)
sunbeam cluster bootstrap
```

## Common Pitfalls

### Hardware Configuration Steps

When adding hardware-specific steps (NICs, PCI devices):
- **Never** hardcode device names - always prompt or use manifest
- Validate via Juju actions on `openstack-hypervisor` unit (e.g., `fetch-nics` action)
- Store per-node config in clusterd with node name as key
- Example: `LocalConfigSRIOVStep` in `sunbeam/provider/local/steps.py`

### Juju Unit/Application Confusion

- Applications are deployed charms (e.g., `glance-k8s`)
- Units are instances of applications (e.g., `glance-k8s/0`, `glance-k8s/1`)
- Always get unit from machine: `jhelper.get_unit_from_machine(app, machine_id, model)`
- Actions run on specific units, not applications

### Model vs Controller Operations

- Bootstrap creates controller: `juju bootstrap manual/... sunbeam-controller`
- Models created within controller: `juju add-model openstack-machines`
- Use `CONTROLLER_MODEL = "admin/controller"` constant for controller model
- Never hardcode controller/model names - use deployment properties

### Snap Confinement

When adding new paths or binaries:
- Update `plugs:` section in `snap/snapcraft.yaml`
- Use `$SNAP` for snap-internal paths, `$SNAP_DATA` for mutable state
- Connect interfaces in `docs/deploy-locally-built-snap.md` instructions
- Test in `--dangerous` mode first, then request store permission

## File Organization

- `sunbeam/commands/` - CLI command implementations (Click-based)
- `sunbeam/steps/` - Reusable step implementations (k8s, hypervisor, etc.)
- `sunbeam/provider/local/` - Local deployment provider specifics
- `sunbeam/features/` - Optional features (DNS, telemetry, secrets, etc.)
- `sunbeam/core/` - Core abstractions (juju, manifest, questions, common)
- `cloud/etc/` - Terraform plans for infrastructure deployment
- `snap-wrappers/commands/` - Snap entry point scripts

## Key Dependencies

- **Juju** (content interface from `juju` snap): Charm orchestration
- **Terraform** (bundled in snap): Infrastructure provisioning
- **Python 3.12**: Strict version requirement
- **Rich**: Terminal UI (Console, Status, Prompt)
- **Pydantic**: Configuration validation and manifest parsing
- **dqlite/MicroCluster**: Distributed state (Go component)

## Code Style

Follow Ruff configuration in `pyproject.toml`:
- Max line length: 88
- Google-style docstrings
- Copyright header required: `# SPDX-FileCopyrightText: 2024 - Canonical Ltd`
- License header: `# SPDX-License-Identifier: Apache-2.0`
