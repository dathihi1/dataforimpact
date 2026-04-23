import pandas as pd
import pytest

from src.validation.time_split import rolling_origin_splits, split_time_holdout


def _ts_df(size: int = 12) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ds": pd.date_range("2020-01-01", periods=size, freq="MS"),
            "y": list(range(size)),
        }
    )


def test_split_time_holdout_respects_order_and_sizes():
    df = _ts_df(12)

    train_df, val_df, test_df = split_time_holdout(df, date_col="ds", val_size=2, test_size=2)

    assert len(train_df) == 8
    assert len(val_df) == 2
    assert len(test_df) == 2
    assert train_df["ds"].max() < val_df["ds"].min()
    assert val_df["ds"].max() < test_df["ds"].min()


def test_split_time_holdout_raises_if_not_enough_rows():
    df = _ts_df(4)

    with pytest.raises(ValueError, match="Not enough rows"):
        split_time_holdout(df, date_col="ds", val_size=2, test_size=2)


def test_split_time_holdout_raises_if_date_column_missing():
    df = _ts_df(10)

    with pytest.raises(ValueError, match="Missing date column"):
        split_time_holdout(df, date_col="event_date", val_size=2, test_size=2)


def test_split_time_holdout_raises_if_date_column_not_datetime():
    df = _ts_df(10)
    df["ds"] = df["ds"].dt.strftime("%Y-%m-%d")

    with pytest.raises(TypeError, match="must be datetime64"):
        split_time_holdout(df, date_col="ds", val_size=2, test_size=2)


def test_split_time_holdout_keeps_duplicate_periods_in_single_partition():
    df = pd.DataFrame(
        {
            "ds": pd.to_datetime(
                [
                    "2020-01-01",
                    "2020-01-01",
                    "2020-02-01",
                    "2020-02-01",
                    "2020-03-01",
                    "2020-03-01",
                    "2020-04-01",
                    "2020-04-01",
                    "2020-05-01",
                    "2020-05-01",
                ]
            ),
            "y": list(range(10)),
        }
    )

    train_df, val_df, test_df = split_time_holdout(df, date_col="ds", val_size=1, test_size=1)

    train_periods = set(train_df["ds"].unique())
    val_periods = set(val_df["ds"].unique())
    test_periods = set(test_df["ds"].unique())

    assert train_periods.isdisjoint(val_periods)
    assert val_periods.isdisjoint(test_periods)
    assert train_periods.isdisjoint(test_periods)


def test_rolling_origin_splits_returns_expected_windows():
    df = _ts_df(10)

    splits = rolling_origin_splits(
        df,
        date_col="ds",
        initial_train_size=5,
        horizon=2,
        step=1,
    )

    assert len(splits) == 4
    for split in splits:
        train_df = split["train"]
        val_df = split["val"]
        assert len(train_df) >= 5
        assert len(val_df) == 2
        assert train_df["ds"].max() < val_df["ds"].min()


def test_rolling_origin_splits_raises_when_no_window_possible():
    df = _ts_df(6)

    with pytest.raises(ValueError, match="No rolling windows"):
        rolling_origin_splits(df, date_col="ds", initial_train_size=5, horizon=2)


@pytest.mark.parametrize(
    "val_size,test_size",
    [(0, 2), (2, 0), (-1, 2), (2, -1)],
)
def test_split_time_holdout_raises_for_non_positive_sizes(val_size: int, test_size: int):
    df = _ts_df(10)

    with pytest.raises(ValueError, match="must be > 0"):
        split_time_holdout(df, date_col="ds", val_size=val_size, test_size=test_size)


def test_rolling_origin_splits_raises_if_date_column_missing():
    df = _ts_df(10)

    with pytest.raises(ValueError, match="Missing date column"):
        rolling_origin_splits(df, date_col="event_date", initial_train_size=5, horizon=2)


def test_rolling_origin_splits_raises_if_date_column_not_datetime():
    df = _ts_df(10)
    df["ds"] = df["ds"].dt.strftime("%Y-%m-%d")

    with pytest.raises(TypeError, match="must be datetime64"):
        rolling_origin_splits(df, date_col="ds", initial_train_size=5, horizon=2)


@pytest.mark.parametrize(
    "initial_train_size,horizon,step",
    [(0, 2, 1), (-1, 2, 1), (5, 0, 1), (5, -1, 1), (5, 2, 0), (5, 2, -1)],
)
def test_rolling_origin_splits_raises_for_non_positive_parameters(
    initial_train_size: int,
    horizon: int,
    step: int,
):
    df = _ts_df(10)

    with pytest.raises(ValueError, match="must be > 0"):
        rolling_origin_splits(
            df,
            date_col="ds",
            initial_train_size=initial_train_size,
            horizon=horizon,
            step=step,
        )
