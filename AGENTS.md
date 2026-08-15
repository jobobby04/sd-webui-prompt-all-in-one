# sd-webui-prompt-all-in-one Extension

## Project Structure

```
stable-diffusion-webui-forge-neo/extensions/sd-webui-prompt-all-in-one/
├── scripts/                          # Python backend
│   └── physton_prompt/
│       ├── get_extra_networks.py     # Extra networks API endpoints
│       ├── on_app_started.py         # FastAPI route registration
│       └── ...
├── src/                              # Vue.js frontend source
│   └── src/
│       ├── mixins/
│       │   ├── commonMixin.js        # Core API methods (gradioAPI, loadExtraNetworks)
│       │   └── phystonPrompt/
│       │       └── groupTagsMixin.js # UI group processing (genGroup, folder loading)
│       └── utils/
│           └── gradioAPI.js          # HTTP API client methods
├── javascript/                       # Built output
│   └── main.entry.js                 # Bundled JS (825 KB)
└── AGENTS.md                         # This file
```

## Build Instructions

```bash
cd stable-diffusion-webui-forge-neo/extensions/sd-webui-prompt-all-in-one/src
npm run build
```

Output: `../javascript/main.entry.js` (~825 KB, ~240 KB gzipped)

## Key Files

| File | Purpose |
|------|---------|
| `scripts/physton_prompt/get_extra_networks.py` | Backend API for loading extra networks (lora, lycoris, embeddings) with folder-filtered loading |
| `scripts/physton_prompt/on_app_started.py` | FastAPI route registration for all `/physton_prompt/*` endpoints |
| `src/src/mixins/commonMixin.js` | Core data loading - `loadExtraNetworks()` (dirs), `loadExtraNetworksItems(name, dirname)` (folder items) |
| `src/src/mixins/phystonPrompt/groupTagsMixin.js` | UI processing - `genGroup()` builds folder tabs, `_loadFolderItems()` triggers lazy loading |
| `src/src/utils/gradioAPI.js` | HTTP client - `getExtraNetworksDirs()`, `getExtraNetworksItems()`, `loadExtraNetworksItems()` |

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /physton_prompt/get_extra_networks_dirs` | Returns `{name, title, dirs: [...]}` - page metadata and folder list |
| `GET /physton_prompt/get_extra_networks_items?name=lora&dirname=folder` | Returns items filtered by extra network type and folder |
| `GET /physton_prompt/get_extra_networks` | Returns all items (original endpoint, loads everything) |

## Data Flow

1. **Initial load**: `commonMixin._loadExtraNetworks()` → calls `getExtraNetworksDirs()` → stores `extraNetworks = [{name, title, dirs: [], items: {}}]`
2. **Folder selection**: User clicks folder → `subGroupTagsActive` watch triggers `_loadFolderItems()` → calls `loadExtraNetworksItems(name, dirname)` → updates `extraNetworks.items[dirname]`
3. **UI update**: `extraNetworks` change triggers `genGroup()` → creates folder-level groups with loaded items → displays in UI
4. **Refresh**: `onClickGroupExtraNetworkRefresh()` → deletes `extraNetworks.items[dirname]` → reloads items → refreshes folder list via `_refreshDirs()`

## State Management

- `extraNetworks`: Array of `{name, title, dirs: [], items: {dirname: [...]}}` - passed as prop to PhystonPrompt component
- `loras`, `lycos`, `embeddings`: Local data properties (`_loras`, `_lycos`, `_embeddings`) - lookup maps for tag validation
- `groupTagsProcessed`: Generated from `genGroup()` - drives the UI tab structure

## Important Notes

- `list_items()` returns a generator, must convert to list with `list()` before using `len()` or indexing
- Props (`loras`, `lycos`, `embeddings`) are readonly - use local data properties (`_loras`, etc.) and emit `update:` events
- `_loadExtraNetworks()` checks `hasLoadedItems` to prevent overwriting loaded folder data
- `genGroup()` uses `extraNetwork.dirs` as source of truth for folder names - ensures all folders show even if not loaded
- Path normalization: all paths converted to forward slashes and normalized with `os.path.normpath()` before comparison
