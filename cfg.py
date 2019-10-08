def _get_default_cfg_path() -> Path:  
    if sys.platform == "win32":
        p = Path("C:/Program Files (x86)")
    elif sys.platform == "darwin":
        p = Path.home() / "Library/Application Support"
    elif sys.platform == "linux":
        p = Path.home()
    else:
        raise NotImplementedError("Hero grid directory auto detection is not supported for your OS!")  
    
    p = p / "Steam/userdata"

    # Choose random subdirectory if no User ID is specified.
    if not Config.USER_ID:
        p = random.choice([d for d in p.iterdir() if d.is_dir()])
    else:
        p = p / str(Config.USER_ID)

    return p / "570/remote/cfg"


def get_cfg_path(path: Optional[str]) -> Path:
    if not path:
        cfg_path = _get_default_cfg_path()
    else:
        cfg_path = Path(path)
    if not cfg_path.exists():
        raise ValueError(f"User cfg directory '{cfg_path}' does not exist!")
    return cfg_path


def update_config(grid: dict, config_name: str, path: Path) -> None:
    """Updates hero grid config file in Steam userdata directory."""
    p = path/"hero_grid_config.json"
    
    # NOTE: This whole block is due a refactor
    
    # Append to existing config if a config exists
    if p.exists():
        configs = json.load(p.open())
        for idx, c in enumerate(configs["configs"]): # Enumerate to get index
            # Update existing hero grid if one exists
            if c["config_name"] == config_name:
                configs["configs"][idx] = grid
                break
        else:
            configs["configs"].append(grid)
        conf = configs
    else:
        conf = copy.deepcopy(CONFIG_BASE)
        conf["configs"].append(grid)
    _save_config(conf)

def _save_config(config: dict) -> None:
    with open(path/"hero_grid_config.json", "w") as f:
        json_data = json.dumps(config, indent="\t")
        f.write(json_data)