"""Application-level workflows for MCore UAV projects."""

from dataclasses import dataclass
from pathlib import Path

from app.models.aircraft import Aircraft
from app.services.project_io import save_aircraft
from app.services.validation import ValidationResult, validate_aircraft


@dataclass(frozen=True)
class ProjectCreateResult:
    """Result of the MCore project creation workflow."""

    created: bool
    path: Path
    validation: ValidationResult


@dataclass(frozen=True)
class ProjectUpdateResult:
    """Result of the MCore project update workflow."""

    updated: bool
    path: Path
    validation: ValidationResult


def create_project(
    aircraft: Aircraft,
    path: str | Path,
) -> ProjectCreateResult:
    """Validate and save an aircraft project."""

    project_path = Path(path)

    validation = validate_aircraft(aircraft)

    if not validation.valid:
        return ProjectCreateResult(
            created=False,
            path=project_path,
            validation=validation,
        )

    save_aircraft(
        aircraft,
        project_path,
    )

    return ProjectCreateResult(
        created=True,
        path=project_path,
        validation=validation,
    )


def update_project(
    aircraft: Aircraft,
    path: str | Path,
) -> ProjectUpdateResult:
    """Validate and update an existing aircraft project."""

    project_path = Path(path)

    validation = validate_aircraft(aircraft)

    if not validation.valid:
        return ProjectUpdateResult(
            updated=False,
            path=project_path,
            validation=validation,
        )

    save_aircraft(
        aircraft,
        project_path,
    )

    return ProjectUpdateResult(
        updated=True,
        path=project_path,
        validation=validation,
    )
