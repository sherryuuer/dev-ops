import json
from typing import Dict, List, Set
from copy import deepcopy

from google.cloud import dataform_v1beta1, storage

SCHEDULE_TAG_PREFIX = "sche_"
SCHEMA_TAG_PREFIX = "ds_"


class ManifestGenerator:
    def __init__(self, client, parent):
        """
        Args:
            client (dataform_v1beta1.DataformClient): dataformクライアント
            parent (str): 対象のdataformのrootリポジトリ
        """
        self.client = client
        self.parent = parent

    def _get_compilation_result(self):
        """
        dataform定義のコンパイル結果情報を取得する

        Returns:
            object: コンパイル結果情報
        """
        compilation_result = dataform_v1beta1.CompilationResult(git_commitish="main")
        request = dataform_v1beta1.CreateCompilationResultRequest(
            parent=self.parent, 
            compilation_result=compilation_result
        )
        return self.client.create_compilation_result(request)

    def _get_compilation_result_actions(self, compile_result_name):
        """
        dataformのアクション詳細情報を取得する

        Args:
            compile_result_name (str): コンパイル結果情報名

        Returns:
            object: アクション詳細情報のページャー
        """
        query_request = dataform_v1beta1.QueryCompilationResultActionsRequest(
            name=compile_result_name
        )
        return self.client.query_compilation_result_actions(request=query_request)

    def _get_schedule_tags(self, action_type):
        """
        tagsからスケジュール用のtagを取得する

        Args:
            action_type (object): dataformのactionオブジェクト

        Returns:
            set: スケジュール用のtag一覧
        """
        tags = [tag for tag in action_type.tags]
        return {tag for tag in tags if tag.startswith(SCHEDULE_TAG_PREFIX)}

    def _create_list_from_tags(self, tags, prefix):
        """
        prefixによってtagsからリストを作る

        Args:
            tags (list): tagリスト
            prefix (str): prefix

        Returns:
            list: prefixより作ったリスト
        """
        return [tag for tag in tags if tag.startswith(prefix)]

    def _create_initial_manifest_structure(self, compilation_result_actions_pages):
        """
        初期化のマニフェストJSONファイルのフォーマットを作成する

        Args:
            compilation_result_actions_pages (object): アクション詳細情報のページャー

        Returns:
            dict: manifestファイルのフォーマット
        """
        schedule_tags = set()
        for action in compilation_result_actions_pages:
            relation = getattr(action, "relation", None)
            operations = getattr(action, "operations", None)

            if not relation and not operations:
                continue

            schedule_tags |= self._get_schedule_tags(relation or operations)

        manifest_structure = {"schedule": {}}
        for schedule_tag in schedule_tags:
            manifest_structure["schedule"][schedule_tag] = {
                "actions": {},
                "all_schema_tags": [],
            }

        return manifest_structure

    def _set_action_data(self, action_type):
        """
        アクションごとの詳細情報を作成する

        Args:
            action_type (object): dataformのactionオブジェクト

        Returns:
            dict: アクションの詳細情報
        """
        action_data = {}
        tags = list(action_type.tags)
        action_data["action_type"] = "relation"
        action_data["dependency_targets"] = [
            f"{dt.database}.{dt.schema}.{dt.name}"
            for dt in action_type.dependency_targets
        ]
        action_data["tags"] = tags
        action_data["schema_tags"] = self._create_list_from_tags(
            tags, SCHEMA_TAG_PREFIX
        )
        action_data["schedule_tags"] = self._get_schedule_tags(action_type)

        return action_data

    def _remove_redundant_schema_tags(self, data, dependency_targets, tags):
        """
        依存関係用のスキーマタグをキレイにする
        upstreamのDMを辿って不要な依存関係（スキーマタグ）を削除する

        Args:
            data (dict): マニフェストデータ
            dependency_targets (list): upstreamのDMリスト
            tags (list): tagのリスト

        Returns:
            list: tagのリスト
        """
        if not dependency_targets:
            return list(tags)

        for d_target in dependency_targets:
            tags = self._remove_redundant_schema_tags(
                data,
                data[d_target].get('dependency_targets', None),
                set(tags) - set(data[d_target]['schema_tags'])
            )

        return list(tags)

    def create_manifest(self):
        """
        dataformのマニフェストファイル（DM間の依存関係設定ファイル）を加工・作成する

        Return:
            dict: 作成したマニフェスト
        """
        compile_result = self._get_compilation_result()
        compilation_result_actions_pages = self._get_compilation_result_actions(
            compile_result.name
        )
        manifest_structure = self._create_initial_manifest_structure(
            compilation_result_actions_pages
        )

        for action in compilation_result_actions_pages:
            relation = getattr(action, "relation", None)
            operations = getattr(action, "operations", None)

            if not relation and not operations:
                continue

            target = f"{action.target.database}.{action.target.schema}.{action.target.name}"
            action_data = self._set_action_data(relation or operations)

            if not action_data["schedule_tags"]:
                manifest_structure["schedule"]["sche_daily"]["actions"][
                    target
                ] = action_data
            else:
                for schedule_tag in action_data["schedule_tags"]:
                    manifest_structure["schedule"][schedule_tag]["actions"][
                        target
                    ] = deepcopy(action_data)

        for schedule, value in manifest_structure["schedule"].items():
            all_schema_tags = set()
            for v in value["actions"].values():
                v["dependency_targets"] = list(
                    set(v["dependency_targets"]) & set(value["actions"].keys())
                )
                v["schema_tags"] = self._remove_redundant_schema_tags(
                    value["actions"], v["dependency_targets"], set(v["schema_tags"])
                )
                all_schema_tags |= set(v["schema_tags"])
                v["schedule_tags"] = list(v["schedule_tags"])
            value["all_schema_tags"] = list(all_schema_tags)

        manifest = {
            "compile_response_name": compile_result.name,
            "schedule": manifest_structure["schedule"],
        }

        return manifest

    def save_manifest(self, manifest, dag_bucket, manifest_path):
        """
        dataformのマニフェストファイル（DM間の依存関係設定ファイル）を保存する

        Args:
            dag_bucket (str): ファイル保存先のバケット
            manifest_path (str): ファイル保存詳細パス
        """
        storage_client = storage.Client()
        bucket = storage_client.bucket(dag_bucket)
        blob = bucket.blob(manifest_path)
        blob.upload_from_string(json.dumps(manifest, indent=4))


def create_and_save_manifest(parent, dag_bucket, manifest_path):
    """
    dataform APIで必要なデータを取得してマニフェストファイルを作成する
    対象のGCSバケットにファイルを保存する

    Args:
        parent (str): 対象のdataformのrootリポジトリ
        dag_bucket (str): ファイル保存先のバケット
        manifest_path (str): ファイル保存詳細パス
    """
    client = dataform_v1beta1.DataformClient()
    generator = ManifestGenerator(client, parent)
    manifest = generator.create_manifest()
    generator.save_manifest(manifest, dag_bucket, manifest_path)