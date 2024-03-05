from .icb_apply_distribution_functions import IcebergCalving


def prep_icebergs(config):
    if "fesom" in config["general"]["valid_model_names"]:
        if config["general"].get("with_icb", False) and config["fesom"].get(
            "use_icesheet_coupling", False
        ):
            # if not config["general"].get("iterative_coupling", False):
            config = update_icebergs(config)
            if config["general"].get("run_number", 0) == 1:
                if not os.path.isfile(
                    config["general"]["experiment_couple_dir"]
                    + "/num_non_melted_icb_file"
                ):
                    with open(
                        config["general"]["experiment_couple_dir"]
                        + "/num_non_melted_icb_file",
                        "w",
                    ) as f:
                        f.write("0")
            else:
                num_lines = sum(
                    1
                    for line in open(
                        os.path.join(
                            config["fesom"]["restart_in_sources"]["icb_restart_ISM"]
                        )
                    )
                )
                with open(
                    config["general"]["experiment_couple_dir"]
                    + "/num_non_melted_icb_file",
                    "w",
                ) as f:
                    f.write(str(num_lines))

        return config


def update_icebergs(config):
    if (
        config["general"].get("with_icb", False)
        and config["fesom"].get("update_icebergs", False)
        and config["general"]["run_number"] > 1
    ):
        print("* starting update icebergs")
        icb_script = config["fesom"].get("icb_script", "")
        disch_file = config["fesom"].get("disch_file", "")
        iceberg_dir = config["fesom"].get(
            "iceberg_dir", config["general"]["experiment_couple_dir"]
        )
        mesh_dir = config["fesom"][
            "mesh_dir"
        ]  # ["namelist_changes"]["namelist.config"]["paths"]["meshpath"]
        basin_file = config["fesom"].get("basin_file", "")
        icb_restart_file = config["fesom"]["restart_in_sources"].get("icb_restart", "")
        scaling_factor = config["fesom"].get("scaling_factor", [1, 1, 1, 1, 1, 1])

        print(" * use scaling factors ", scaling_factor)
        ib = IcebergCalving(
            disch_file,
            mesh_dir,
            iceberg_dir,
            basin_file,
            icb_restart_file,
            scaling_factor=scaling_factor,
        )
        ib.create_dataframe()
        ib._icb_generator()
    return config
