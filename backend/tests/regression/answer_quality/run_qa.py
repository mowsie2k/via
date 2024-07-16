import json
import os
import time

import yaml

from tests.regression.answer_quality.api_utils import check_if_query_ready
from tests.regression.answer_quality.api_utils import get_answer_from_query
from tests.regression.answer_quality.cli_utils import get_current_commit_sha
from tests.regression.answer_quality.cli_utils import get_docker_container_env_vars

RESULTS_FILENAME = "results.jsonl"
METADATA_FILENAME = "metadata.yaml"


def _update_results_file(output_folder_path: str, qa_output: dict) -> None:
    output_file_path = os.path.join(output_folder_path, RESULTS_FILENAME)
    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write(json.dumps(qa_output) + "\n")
        file.flush()


def _update_metadata_file(test_output_folder: str, count: int) -> None:
    metadata_path = os.path.join(test_output_folder, METADATA_FILENAME)
    with open(metadata_path, "r", encoding="utf-8") as file:
        metadata = yaml.safe_load(file)

    metadata["number_of_questions_asked"] = count
    with open(metadata_path, "w", encoding="utf-8") as yaml_file:
        yaml.dump(metadata, yaml_file)


def _read_questions_jsonl(questions_file_path: str) -> list[dict]:
    questions = []
    with open(questions_file_path, "r") as file:
        for line in file:
            json_obj = json.loads(line)
            questions.append(json_obj)
    return questions


def _get_test_output_folder(config: dict) -> str:
    base_output_folder = os.path.expanduser(config["output_folder"])
    if config["run_suffix"]:
        base_output_folder = os.path.join(
            base_output_folder, ("test" + config["run_suffix"]), "relari_output"
        )
    else:
        base_output_folder = os.path.join(base_output_folder, "no_defined_suffix")

    counter = 1
    run_suffix = config["run_suffix"][1:]
    output_folder_path = os.path.join(base_output_folder, f"{run_suffix}_run_1")
    while os.path.exists(output_folder_path):
        output_folder_path = os.path.join(
            output_folder_path.replace(
                f"{run_suffix}_run_{counter-1}", f"{run_suffix}_run_{counter}"
            ),
        )
        counter += 1

    os.makedirs(output_folder_path, exist_ok=True)

    return output_folder_path


def _initialize_files(config: dict) -> tuple[str, list[dict]]:
    test_output_folder = _get_test_output_folder(config)

    questions = _read_questions_jsonl(config["questions_file"])

    metadata = {
        "commit_sha": get_current_commit_sha(),
        "run_suffix": config["run_suffix"],
        "test_config": config,
        "number_of_questions_in_dataset": len(questions),
    }

    env_vars = get_docker_container_env_vars(config["run_suffix"])
    if env_vars["ENV_SEED_CONFIGURATION"]:
        del env_vars["ENV_SEED_CONFIGURATION"]
    if env_vars["GPG_KEY"]:
        del env_vars["GPG_KEY"]
    if metadata["config"]["llm"]["api_key"]:
        del metadata["config"]["llm"]["api_key"]
    metadata.update(env_vars)
    metadata_path = os.path.join(test_output_folder, METADATA_FILENAME)
    print("saving metadata to:", metadata_path)
    with open(metadata_path, "w", encoding="utf-8") as yaml_file:
        yaml.dump(metadata, yaml_file)

    return test_output_folder, questions


def _process_and_write_query_results(config: dict) -> None:
    test_output_folder, questions = _initialize_files(config)
    print("saving test results to folder:", test_output_folder)

    while not check_if_query_ready(config["run_suffix"]):
        time.sleep(5)

    if config["limit"] is not None:
        questions = questions[: config["limit"]]
    count = 1
    for question_data in questions:
        print(f"On question number {count}")

        query = question_data["question"]
        print(f"query: {query}")
        context_data_list, answer = get_answer_from_query(
            query=query,
            run_suffix=config["run_suffix"],
        )

        if not context_data_list:
            print("No answer or context found")
        else:
            print(f"answer: {answer[:50]}...")
            print(f"{len(context_data_list)} context docs found")
        print("\n")

        output = {
            "question_data": question_data,
            "answer": answer,
            "context_data_list": context_data_list,
        }

        _update_results_file(test_output_folder, output)
        _update_metadata_file(test_output_folder, count)
        count += 1


def run_qa_test_and_save_results(run_suffix: str = "") -> None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "search_test_config.yaml")
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    if not isinstance(config, dict):
        raise TypeError("config must be a dictionary")

    if not run_suffix:
        run_suffix = config["existing_test_suffix"]

    config["run_suffix"] = run_suffix
    _process_and_write_query_results(config)


if __name__ == "__main__":
    """
    To run a different set of questions, update the questions_file in search_test_config.yaml
    If there is more than one instance of Danswer running, specify the suffix in search_test_config.yaml
    """
    run_qa_test_and_save_results()
