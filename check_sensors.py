"""Script to check equipment calibration status across multiple file formats."""

import json
import typing
from pathlib import Path

import pandas as pd
import yaml


def load_config(config_path: Path) -> dict[str, typing.Any]:
    """Read configuration settings from a YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    if config is None:
        return {}
    return config


def find_overdue_sensors(
    sensors_file: Path, calibrations_file: Path, max_days: int
) -> list[dict[str, typing.Any]]:
    """Join sensor locations with calibration logs and filter overdue sensors."""
    df_sensors: pd.DataFrame = pd.read_excel(sensors_file)
    df_calibrations: pd.DataFrame = pd.read_csv(calibrations_file)

    merged_df: pd.DataFrame = pd.merge(df_sensors, df_calibrations, on="sensor_id")

    overdue_df: pd.DataFrame = merged_df[
        merged_df["days_since_calibration"] > max_days
    ]

    records = overdue_df.to_dict(orient="records")
    return typing.cast(list[dict[str, typing.Any]], records)


def export_to_json(data: list[dict[str, typing.Any]], output_path: Path) -> None:
    """Export dataset to a formatted JSON file."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main() -> None:
    """Execute the check_sensors pipeline."""
    base_dir = Path(__file__).parent

    config_path = base_dir / "config.yml"
    sensors_path = base_dir / "sensors.xlsx"
    calibrations_path = base_dir / "calibrations.csv"

    config = load_config(config_path)
    max_days = config["max_days_since_calibration"]
    output_path = base_dir / config["output_file"]

    overdue_sensors = find_overdue_sensors(sensors_path, calibrations_path, max_days)
    export_to_json(overdue_sensors, output_path)

    print(f"Exported {len(overdue_sensors)} overdue sensor(s) to '{output_path.name}'.")


if __name__ == "__main__":
    main()