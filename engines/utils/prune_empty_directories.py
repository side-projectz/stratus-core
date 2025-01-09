def prune_empty_directories(structure: dict) -> dict:
    keys_to_delete = []
    for key, value in structure.items():
        if isinstance(value, dict):
            # Recur into subdirectories
            pruned = prune_empty_directories(value)
            if not pruned:
                # If empty after pruning, mark for removal
                keys_to_delete.append(key)
            else:
                structure[key] = pruned

    # Remove empty directories
    for k in keys_to_delete:
        del structure[k]

    return structure
