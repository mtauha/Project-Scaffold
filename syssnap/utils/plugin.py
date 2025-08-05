import os
import importlib.util


def load_plugins(plugin_dir):
    plugins = {}
    if not os.path.exists(plugin_dir):
        return plugins
    for fname in os.listdir(plugin_dir):
        if fname.endswith(".py"):
            mod_name = fname[:-3]
            spec = importlib.util.spec_from_file_location(
                mod_name, os.path.join(plugin_dir, fname)
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "collect"):
                plugins[mod_name] = mod
    return plugins
