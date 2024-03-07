import f90nml
import os

from .icb_apply_distribution_functions import IcebergCalving

from esm_runscripts.namelists import Namelist

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
            seed=int(str(config["general"]["current_date"].year) + str(config["general"]["current_date"].month)) 
        )
        ib.create_dataframe()
        ib._icb_generator()
    return config


def apply_iceberg_calving_to_namelists(config):
    """
    Calculates new number of icebergs when icesheet coupling is turned on

    Relevant configuration entries:
    """
    if "fesom" in config["general"]["valid_model_names"] and config["fesom"].get(
        "with_icb", False
    ):
        # Get the fesom config namelist:
        nml = config["fesom"]["namelists"]["namelist.config"]
        # Get the current icebergs chapter or make a new empty one:
        icebergs = nml.get("icebergs", f90nml.namelist.Namelist())
        # Determine if icesheet coupling is enabled:
        if config["fesom"].get("use_icesheet_coupling", False):
            icebergs["use_icesheet_coupling"] = True
            if os.path.isfile(
                config["fesom"]["input_sources"]["num_non_melted_icb_file"]
            ):
                print(
                    " * using this file: ",
                    config["fesom"]["input_sources"]["num_non_melted_icb_file"],
                )
                with open(
                    config["fesom"]["input_sources"]["num_non_melted_icb_file"]
                    # config["fesom"]["iceberg_dir"] + "/num_non_melted_icb_file"
                ) as f:
                    ib_num_old = [
                        int(line.strip()) for line in f.readlines() if line.strip()
                    ][0]
            elif config["general"]["run_number"] == 1:
                ib_num_old = 0
            else:
                print("Something went wrong! Continue without old icebergs.")
                ib_num_old = 0

            print(" * iceberg_dir = ", config["fesom"].get("iceberg_dir"))
            ib_num_new = sum(
                1 for line in open(config["fesom"]["input_sources"].get("length"))
            )
            icebergs["ib_num"] = ib_num_old + ib_num_new
            nml["icebergs"] = icebergs

            config["fesom"] = Namelist.nmls_modify(config["fesom"])
            config["fesom"] = Namelist.nmls_finalize(
                config["fesom"], config["general"]["verbose"]
            )

    return config
