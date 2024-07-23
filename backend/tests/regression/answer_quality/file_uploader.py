import os
import tempfile
import time
import zipfile
from pathlib import Path
from types import SimpleNamespace

import yaml

from tests.regression.answer_quality.api_utils import check_indexing_status
from tests.regression.answer_quality.api_utils import create_cc_pair
from tests.regression.answer_quality.api_utils import create_connector
from tests.regression.answer_quality.api_utils import create_credential
from tests.regression.answer_quality.api_utils import run_cc_once
from tests.regression.answer_quality.api_utils import upload_file
from tests.regression.answer_quality.cli_utils import restart_vespa_container


def unzip_and_get_file_paths(zip_file_path: str) -> list[str]:
    persistent_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(persistent_dir)

    return [str(path) for path in Path(persistent_dir).rglob("*") if path.is_file()]


def create_temp_zip_from_files(file_paths: list[str]) -> str:
    persistent_dir = tempfile.mkdtemp()
    zip_file_path = os.path.join(persistent_dir, "temp.zip")

    with zipfile.ZipFile(zip_file_path, "w") as zip_file:
        for file_path in file_paths:
            zip_file.write(file_path, Path(file_path).name)

    return zip_file_path


def upload_test_files(zip_file_path: str, run_suffix: str) -> None:
    print("zip:", zip_file_path)
    file_paths = upload_file(run_suffix, zip_file_path)

    conn_id = create_connector(run_suffix, file_paths)
    cred_id = create_credential(run_suffix)

    create_cc_pair(run_suffix, conn_id, cred_id)
    run_cc_once(run_suffix, conn_id, cred_id)


def manage_file_upload(zip_file_path: str, run_suffix: str) -> None:
    unzipped_file_paths = unzip_and_get_file_paths(zip_file_path)
    total_file_count = len(unzipped_file_paths)

    while True:
        doc_count, ongoing_index_attempts = check_indexing_status(run_suffix)

        if not doc_count:
            print("No docs indexed, waiting for indexing to start")
            upload_test_files(zip_file_path, run_suffix)
        elif ongoing_index_attempts:
            print(
                f"{doc_count} docs indexed but waiting for ongoing indexing jobs to finish..."
            )
        elif doc_count < total_file_count:
            print(f"No ongooing indexing attempts but only {doc_count} docs indexed")
            print("Restarting vespa...")
            restart_vespa_container(run_suffix)
            print(f"Rerunning with {total_file_count - doc_count} missing docs")
            remaining_files = unzipped_file_paths[doc_count:]
            print(f"Grabbed last {len(remaining_files)} docs to try agian")
            temp_zip_file_path = create_temp_zip_from_files(remaining_files)
            upload_test_files(temp_zip_file_path, run_suffix)
            os.unlink(temp_zip_file_path)
        else:
            print(f"Successfully uploaded {doc_count} docs!")
            break

        time.sleep(10)

    for file in unzipped_file_paths:
        os.unlink(file)


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "search_test_config.yaml")
    with open(config_path, "r") as file:
        config = SimpleNamespace(**yaml.safe_load(file))
    file_location = config.zipped_documents_file
    run_suffix = config.existing_test_suffix
    manage_file_upload(file_location, run_suffix)
