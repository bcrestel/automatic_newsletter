import shutil

import pandas as pd
import pytest

from src.saving.database import UNIQUE_ID_COL
from src.saving.main import runner

PATH_TO_LOG_PARQUET = "/home/src/tests/data/test_log_report.parquet"
TMP_PATH_TO_PARQUET = "test.parquet"


def prep_no_file(path_tmp):
    df_log_report = pd.read_parquet(PATH_TO_LOG_PARQUET)
    runner(df_scored_news_stories_new=df_log_report, path_to_db=path_tmp)
    df_created_by_runner = pd.read_parquet(path_tmp)
    return df_log_report, df_created_by_runner


def test_no_file_1(tmp_path):
    # Check we have the same dataframes before and after
    df_raw = pd.read_parquet(PATH_TO_LOG_PARQUET)
    df_log_report, df_created_by_runner = prep_no_file(tmp_path / TMP_PATH_TO_PARQUET)
    assert len(df_raw) == len(df_log_report)
    assert len(df_raw.columns) + 1 == len(df_log_report.columns)
    assert (
        df_log_report.shape == df_created_by_runner.shape
    ), f"{df_log_report.shape} vs {df_created_by_runner.shape}"
    assert df_log_report.equals(df_created_by_runner)


def test_no_file_2(tmp_path):
    # Check unique_id is in the right dataframes
    df_raw = pd.read_parquet(PATH_TO_LOG_PARQUET)
    assert UNIQUE_ID_COL not in df_raw.columns, df_raw.columns
    df_log_report, df_created_by_runner = prep_no_file(tmp_path / TMP_PATH_TO_PARQUET)
    assert UNIQUE_ID_COL in df_log_report.columns, df_log_report.columns
    assert UNIQUE_ID_COL in df_created_by_runner.columns, df_created_by_runner.columns


def test_no_file_3(tmp_path):
    # Check unique_id is unique
    _, df_created_by_runner = prep_no_file(tmp_path / TMP_PATH_TO_PARQUET)
    unique_ids = df_created_by_runner[UNIQUE_ID_COL].unique()
    assert len(unique_ids) == len(df_created_by_runner)


def prep_existing_file(path_tmp, add_unique_id_col=False):
    if add_unique_id_col:
        df_tmp = pd.read_parquet(PATH_TO_LOG_PARQUET)
        df_tmp[UNIQUE_ID_COL] = range(len(df_tmp))
        df_tmp.to_parquet(path_tmp)
    else:
        shutil.copy(PATH_TO_LOG_PARQUET, path_tmp)
    df_log_report = pd.read_parquet(path_tmp)
    df_news_stories = pd.read_parquet(PATH_TO_LOG_PARQUET)
    runner(df_scored_news_stories_new=df_news_stories, path_to_db=path_tmp)
    df_created_by_runner = pd.read_parquet(path_tmp)
    return df_log_report, df_created_by_runner


def test_existing_file_1(tmp_path):
    # Check this raises an error as the UNIQUE_ID_COL is not defined
    with pytest.raises(KeyError):
        _, _ = prep_existing_file(tmp_path / TMP_PATH_TO_PARQUET)


def test_existing_file_2(tmp_path):
    # Check dimensions of the dataframes before and after
    df_log_report, df_created_by_runner = prep_existing_file(
        tmp_path / TMP_PATH_TO_PARQUET, add_unique_id_col=True
    )
    assert len(df_log_report.columns) == len(
        df_created_by_runner.columns
    ), f"{df_log_report.columns} vs {df_created_by_runner.columns}"
    assert 2 * len(df_log_report) == len(df_created_by_runner)


def test_existing_file_2(tmp_path):
    # Check unique_id is in both dataframes
    df_log_report, df_created_by_runner = prep_existing_file(
        tmp_path / TMP_PATH_TO_PARQUET, add_unique_id_col=True
    )
    assert UNIQUE_ID_COL in df_log_report.columns, df_log_report.columns
    assert UNIQUE_ID_COL in df_created_by_runner.columns, df_created_by_runner.columns


def test_existing_file_3(tmp_path):
    # Check unique_id is unique
    _, df_created_by_runner = prep_existing_file(
        tmp_path / TMP_PATH_TO_PARQUET, add_unique_id_col=True
    )
    unique_ids = df_created_by_runner[UNIQUE_ID_COL].unique()
    assert len(unique_ids) == len(df_created_by_runner)


def test_existing_file_4(tmp_path):
    # Check we have the correct dataframes
    df_log_report, df_created_by_runner = prep_existing_file(
        tmp_path / TMP_PATH_TO_PARQUET, add_unique_id_col=True
    )
    existing_ids = df_log_report[UNIQUE_ID_COL]
    df_created_by_runner = df_created_by_runner.set_index(UNIQUE_ID_COL)
    df_existing = df_created_by_runner.loc[existing_ids]
    df_log_report = df_log_report.set_index(UNIQUE_ID_COL).loc[existing_ids]
    assert df_log_report.equals(
        df_existing
    ), f"{df_log_report[UNIQUE_ID_COL]} vs {df_existing[UNIQUE_ID_COL]}"
    new_ids = df_created_by_runner.index.difference(df_existing.index)
    assert df_log_report.reset_index(drop=True).equals(
        df_created_by_runner.loc[new_ids].reset_index(drop=True)
    )
