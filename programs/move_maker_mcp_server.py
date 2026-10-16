<<<<<<< HEAD
from __future__ import annotations

import base64
import io
import math
import re
from typing import Any, Literal, Optional

import numpy as np
import pandas as pd


URL = "https://raw.githubusercontent.com/stepodo/sas-ram-hackathon/main/data/movie_database.csv"

movies_df: Optional[pd.DataFrame] = pd.read_csv(
    URL,
    dtype={
        "movie_id": "string",
        "name": "string",
        "rating": "string",
        "genre": "string",
        "year": "Int64",
        "released": "string",
        "score": "float64",
        "votes": "Int64",
        "director": "string",
        "writer": "string",
        "star": "string",
        "country": "string",
        "budget": "float64",
        "revenue": "float64",
        "company": "string",
        "runtime": "Int64",
        "release_date": "string",
        "release_month": "Int64",
        "release_year": "Int64",
        "release_quarter": "Int64",
        "release_week": "Int64",
        "release_dayofweek": "Int64",
        "is_weekend_release": "bool",
        "is_summer_release": "bool",
        "is_awards_season": "bool",
        "is_holiday_season": "bool",
        "log_budget": "float64",
        "log_revenue": "float64",
        "profit": "float64",
        "roi": "float64",
        "revenue_budget_ratio": "float64",
        "profit_margin_proxy": "float64",
    },
)


ALLOWED_COLUMNS = {
    "name", "rating", "genre", "year", "released", "score", "votes",
    "director", "writer", "star", "country", "budget", "revenue", "company",
    "runtime", "release_date", "release_month", "release_year",
    "release_quarter", "release_week", "release_dayofweek",
    "is_weekend_release", "is_summer_release", "is_awards_season",
    "is_holiday_season", "log_budget", "log_revenue", "profit", "roi",
    "revenue_budget_ratio", "profit_margin_proxy",
}

NUMERIC_COLUMNS = {
    "year", "score", "votes", "budget", "revenue", "runtime", "release_month",
    "release_year", "release_quarter", "release_week", "release_dayofweek",
    "is_weekend_release", "is_summer_release", "is_awards_season",
    "is_holiday_season", "log_budget", "log_revenue", "profit", "roi",
    "revenue_budget_ratio", "profit_margin_proxy",
}

CATEGORICAL_COLUMNS = {
    "name", "rating", "genre", "released", "director", "writer", "star",
    "country", "company",
}

TIME_DIMENSIONS = {
    "year", "release_year", "release_month", "release_quarter", "release_week",
    "release_dayofweek", "is_weekend_release", "is_summer_release",
    "is_awards_season", "is_holiday_season",
}

AGGREGATIONS = {
    "count", "nunique", "sum", "mean", "median", "min", "max", "std",
}

FILTER_OPERATORS = {
    "=", "eq", "!=", "ne", ">", "gt", ">=", "ge", "<", "lt", "<=", "le",
    "between", "in", "contains", "is_null", "not_null",
}


def set_movies_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    """Bind a live pandas DataFrame to the MCP server."""
    global movies_df

    if not isinstance(df, pd.DataFrame):
        return {
            "status": "error",
            "error_type": "TypeError",
            "message": "df must be a pandas DataFrame.",
            "data": [],
        }

    movies_df = df
    return {
        "status": "ok",
        "message": "DataFrame bound successfully.",
        "rows": int(len(df)),
        "columns": list(df.columns),
        "data": [],
    }


def _df() -> pd.DataFrame:
    if movies_df is None:
        raise RuntimeError(
            "movies_df is not bound. Call set_movies_dataframe(your_dataframe) first."
        )
    return movies_df


def _validate_column(column: str) -> str:
    column = str(column)
    if column not in _df().columns:
        raise ValueError(f"Unknown column: {column}")
    return column


def _json_value(value: Any) -> Any:
    if value is None or value is pd.NA:
        return None

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, (np.floating, float)):
        numeric_value = float(value)
        return numeric_value if math.isfinite(numeric_value) else None

    if isinstance(value, (np.bool_, bool)):
        return bool(value)

    if isinstance(value, (pd.Timestamp, np.datetime64)):
        return pd.Timestamp(value).isoformat()

    return value


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    clean = frame.replace([np.inf, -np.inf], np.nan)
    return [
        {str(key): _json_value(value) for key, value in row.items()}
        for row in clean.to_dict(orient="records")
    ]


def _safe_limit(limit: int, maximum: int = 1000) -> int:
    try:
        limit_int = int(limit)
    except (TypeError, ValueError):
        limit_int = 10
    return max(1, min(limit_int, maximum))


def _normalize_filters(
    filters: Optional[list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Normalize filter objects and accept both 'op' and 'operator'."""
    if not filters:
        return []

    if not isinstance(filters, list):
        raise ValueError("filters must be a list of objects.")

    normalized: list[dict[str, Any]] = []
    allowed_keys = {"column", "op", "operator", "value"}

    for index, item in enumerate(filters):
        if not isinstance(item, dict):
            raise ValueError(f"filters[{index}] must be an object.")

        unknown_keys = set(item.keys()) - allowed_keys
        if unknown_keys:
            raise ValueError(
                f"filters[{index}] contains unsupported key(s): "
                f"{sorted(unknown_keys)}. Allowed keys: {sorted(allowed_keys)}."
            )

        column = item.get("column")
        if not column:
            raise ValueError(f"filters[{index}] must define 'column'.")

        operator = item.get("op", item.get("operator"))
        if operator is None:
            raise ValueError(
                f"filters[{index}] must define 'op' or 'operator'."
            )

        operator = str(operator).lower().strip()
        if operator not in FILTER_OPERATORS:
            raise ValueError(
                f"filters[{index}] has unsupported operator: {operator}. "
                f"Supported operators: {sorted(FILTER_OPERATORS)}."
            )

        normalized.append({
            "column": str(column),
            "op": operator,
            "value": item.get("value"),
        })

    return normalized


def _apply_filters(
    frame: pd.DataFrame,
    filters: Optional[list[dict[str, Any]]],
) -> pd.DataFrame:
    filters = _normalize_filters(filters)

    if not filters:
        return frame.copy()

    result = frame.copy()

    for item in filters:
        column = _validate_column(item["column"])
        operator = item["op"]
        value = item["value"]
        series = result[column]

        if operator in {"=", "eq"}:
            mask = series.eq(value)
        elif operator in {"!=", "ne"}:
            mask = series.ne(value)
        elif operator in {">", "gt"}:
            mask = pd.to_numeric(series, errors="coerce") > float(value)
        elif operator in {">=", "ge"}:
            mask = pd.to_numeric(series, errors="coerce") >= float(value)
        elif operator in {"<", "lt"}:
            mask = pd.to_numeric(series, errors="coerce") < float(value)
        elif operator in {"<=", "le"}:
            mask = pd.to_numeric(series, errors="coerce") <= float(value)
        elif operator == "between":
            if not isinstance(value, (list, tuple)) or len(value) != 2:
                raise ValueError("between requires value=[lower, upper].")
            numeric = pd.to_numeric(series, errors="coerce")
            mask = numeric.between(
                float(value[0]), float(value[1]), inclusive="both"
            )
        elif operator == "in":
            if not isinstance(value, list):
                raise ValueError("in requires a list value.")
            mask = series.isin(value)
        elif operator == "contains":
            mask = series.astype("string").str.contains(
                re.escape(str(value)), case=False, na=False, regex=True
            )
        elif operator == "is_null":
            mask = series.isna()
        elif operator == "not_null":
            mask = series.notna()
        else:
            raise ValueError(f"Unsupported operator: {operator}")

        result = result.loc[mask.fillna(False)]

    return result


def _aggregate(
    frame: pd.DataFrame,
    group_by: list[str],
    metrics: list[dict[str, str]],
) -> pd.DataFrame:
    for column in group_by:
        _validate_column(column)

    if not metrics:
        raise ValueError("At least one metric is required.")

    named_aggs: dict[str, pd.NamedAgg] = {}

    for metric in metrics:
        column = _validate_column(metric["column"])
        aggregation = str(metric["agg"]).lower().strip()

        if aggregation not in AGGREGATIONS:
            raise ValueError(f"Unsupported aggregation: {aggregation}")

        alias = metric.get("alias") or f"{column}_{aggregation}"
        named_aggs[alias] = pd.NamedAgg(column=column, aggfunc=aggregation)

    if group_by:
        return (
            frame.groupby(group_by, dropna=False)
            .agg(**named_aggs)
            .reset_index()
        )

    values = {
        alias: getattr(frame[spec.column], spec.aggfunc)()
        for alias, spec in named_aggs.items()
    }
    return pd.DataFrame([values])


def _search_mask(series: pd.Series, text: Optional[str]) -> pd.Series:
    if not text:
        return pd.Series(True, index=series.index)

    return series.astype("string").str.contains(
        re.escape(str(text)), case=False, na=False
    )


def _ok(
    data: list[dict[str, Any]],
    message: Optional[str] = None,
    **metadata: Any,
) -> dict[str, Any]:
    return {
        "status": "ok",
        "matched_rows": len(data),
        "returned_rows": len(data),
        "data": data,
        "message": message,
        **metadata,
    }


def _error(exc: Exception) -> dict[str, Any]:
    return {
        "status": "error",
        "error_type": type(exc).__name__,
        "message": str(exc),
        "data": [],
    }

#@tool
def get_dataset_schema(sample_rows: int = 5) -> dict[str, Any]:
    """Return shape, data types, null rates, cardinality, ranges, and samples."""
    try:
        df = _df()
        columns: list[dict[str, Any]] = []

        for column in df.columns:
            series = df[column]
            numeric = pd.to_numeric(series, errors="coerce")

            item: dict[str, Any] = {
                "name": column,
                "dtype": str(series.dtype),
                "non_null": int(series.notna().sum()),
                "missing": int(series.isna().sum()),
                "missing_pct": float(series.isna().mean() * 100),
                "unique": int(series.nunique(dropna=True)),
            }

            if numeric.notna().any() and (
                column in NUMERIC_COLUMNS
                or pd.api.types.is_numeric_dtype(series)
            ):
                item["min"] = _json_value(numeric.min())
                item["max"] = _json_value(numeric.max())

            columns.append(item)

        sample = _records(df.head(_safe_limit(sample_rows, 20)))

        return {
            "status": "ok",
            "rows": int(len(df)),
            "columns_count": int(len(df.columns)),
            "columns": columns,
            "sample": sample,
            "message": None,
        }

    except Exception as exc:
        return _error(exc)

#@tool
def search_movies(
    name: Optional[str] = None,
    genre: Optional[str] = None,
    director: Optional[str] = None,
    writer: Optional[str] = None,
    star: Optional[str] = None,
    company: Optional[str] = None,
    country: Optional[str] = None,
    rating: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    limit: int = 20,
) -> dict[str, Any]:
    """Search movies using case-insensitive partial text and year bounds."""
    try:
        df = _df()
        mask = pd.Series(True, index=df.index)

        text_filters = {
            "name": name,
            "genre": genre,
            "director": director,
            "writer": writer,
            "star": star,
            "company": company,
            "country": country,
            "rating": rating,
        }

        for column, text in text_filters.items():
            if text is not None:
                mask &= _search_mask(df[column], text)

        year_column = "release_year" if "release_year" in df.columns else "year"
        years = pd.to_numeric(df[year_column], errors="coerce")

        if year_from is not None:
            mask &= years >= year_from
        if year_to is not None:
            mask &= years <= year_to

        matched = df.loc[mask]
        rows = _records(matched.head(_safe_limit(limit)))

        return {
            "status": "ok",
            "matched_rows": int(mask.sum()),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": {
                **{key: value for key, value in text_filters.items() if value is not None},
                "year_from": year_from,
                "year_to": year_to,
                "limit": limit,
            },
            "message": (
                "No movies matched the supplied criteria."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def get_movie(name: str, limit: int = 10) -> dict[str, Any]:
    """Return exact matches first, then case-insensitive partial matches."""
    try:
        df = _df()
        names = df["name"].astype("string")

        exact = df.loc[names.str.casefold() == name.casefold()]
        partial = df.loc[
            names.str.contains(re.escape(name), case=False, na=False)
        ]

        matched = pd.concat([exact, partial]).loc[
            lambda frame: ~frame.index.duplicated(keep="first")
        ]

        rows = _records(matched.head(_safe_limit(limit, 50)))

        return {
            "status": "ok",
            "query": name,
            "matched_rows": int(len(matched)),
            "returned_rows": len(rows),
            "data": rows,
            "message": (
                f"No movie matched '{name}'."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def filter_movies(
    filters: Optional[list[dict[str, Any]]] = None,
    columns: Optional[list[str]] = None,
    sort_by: Optional[str] = None,
    ascending: bool = False,
    limit: int = 100,
) -> dict[str, Any]:
    """Filter using structured operators and return a JSON object."""
    try:
        normalized_filters = _normalize_filters(filters)
        result = _apply_filters(_df(), normalized_filters)

        if sort_by:
            _validate_column(sort_by)
            result = result.sort_values(
                sort_by, ascending=ascending, na_position="last"
            )

        if columns:
            for column in columns:
                _validate_column(column)
            result = result[columns]

        rows = _records(result.head(_safe_limit(limit)))

        return {
            "status": "ok",
            "matched_rows": int(len(result)),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": normalized_filters,
            "columns_selected": columns,
            "sort_by": sort_by,
            "ascending": ascending,
            "limit": limit,
            "message": (
                "No rows matched the supplied filters."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def rank_movies(
    metric: str,
    n: int = 10,
    ascending: bool = False,
    filters: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    """Rank movies by a numeric metric after optional filtering."""
    try:
        normalized_filters = _normalize_filters(filters)
        _validate_column(metric)

        result = _apply_filters(_df(), normalized_filters).copy()
        result[metric] = pd.to_numeric(result[metric], errors="coerce")

        output_columns = [
            column
            for column in ["name", "release_year", "genre", metric]
            if column in result.columns
        ]

        ranked = (
            result.dropna(subset=[metric])
            .sort_values(metric, ascending=ascending)[output_columns]
            .head(_safe_limit(n, 100))
        )

        rows = _records(ranked)

        return {
            "status": "ok",
            "metric": metric,
            "ascending": ascending,
            "matched_rows": int(len(result.dropna(subset=[metric]))),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": normalized_filters,
            "message": (
                f"No non-null values found for metric '{metric}'."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def aggregate_movies(
    group_by: list[str],
    metrics: list[dict[str, str]],
    filters: Optional[list[dict[str, Any]]] = None,
    sort_by: Optional[str] = None,
    ascending: bool = False,
    limit: int = 50,
) -> dict[str, Any]:
    """Perform safe group-by aggregations and return a JSON object."""
    try:
        normalized_filters = _normalize_filters(filters)
        result = _aggregate(
            _apply_filters(_df(), normalized_filters),
            group_by,
            metrics,
        )

        if sort_by:
            if sort_by not in result.columns:
                raise ValueError(
                    f"Unknown aggregated output column: {sort_by}"
                )
            result = result.sort_values(
                sort_by, ascending=ascending, na_position="last"
            )

        rows = _records(result.head(_safe_limit(limit, 500)))

        return {
            "status": "ok",
            "group_by": group_by,
            "metrics": metrics,
            "matched_rows": int(len(result)),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": normalized_filters,
            "sort_by": sort_by,
            "ascending": ascending,
            "message": (
                "No aggregate rows were produced."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def compare_segments(
    dimension: str,
    metrics: Optional[list[str]] = None,
    filters: Optional[list[dict[str, Any]]] = None,
    top_n: int = 20,
) -> dict[str, Any]:
    """Compare categories using count, median, and mean metrics."""
    try:
        normalized_filters = _normalize_filters(filters)
        _validate_column(dimension)

        metrics = metrics or ["revenue", "profit", "roi", "score"]

        specs: list[dict[str, str]] = [
            {"column": "name", "agg": "count", "alias": "movie_count"}
        ]

        for metric in metrics:
            _validate_column(metric)
            specs.extend([
                {
                    "column": metric,
                    "agg": "median",
                    "alias": f"median_{metric}",
                },
                {
                    "column": metric,
                    "agg": "mean",
                    "alias": f"mean_{metric}",
                },
            ])

        result = _aggregate(
            _apply_filters(_df(), normalized_filters),
            [dimension],
            specs,
        )

        result = result.sort_values(
            "movie_count", ascending=False
        ).head(_safe_limit(top_n, 100))

        rows = _records(result)

        return {
            "status": "ok",
            "dimension": dimension,
            "metrics": metrics,
            "matched_rows": int(len(result)),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": normalized_filters,
            "message": (
                f"No segments found for dimension '{dimension}'."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def analyze_release_timing(
    metric: str = "revenue",
    group_by: str = "release_month",
    statistic: Literal[
        "count", "sum", "mean", "median", "min", "max", "std"
    ] = "median",
    filters: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    """Analyze a metric by an engineered release-calendar dimension."""
    try:
        if group_by not in TIME_DIMENSIONS:
            raise ValueError(
                f"group_by must be one of {sorted(TIME_DIMENSIONS)}."
            )

        _validate_column(metric)

        return aggregate_movies(
            group_by=[group_by],
            metrics=[
                {
                    "column": "name",
                    "agg": "count",
                    "alias": "movie_count",
                },
                {
                    "column": metric,
                    "agg": statistic,
                    "alias": f"{statistic}_{metric}",
                },
            ],
            filters=filters,
            sort_by=group_by,
            ascending=True,
            limit=100,
        )

    except Exception as exc:
        return _error(exc)

#@tool
def describe_metrics(
    columns: list[str],
    filters: Optional[list[dict[str, Any]]] = None,
    percentiles: Optional[list[float]] = None,
) -> dict[str, Any]:
    """Return descriptive statistics for requested numeric columns."""
    try:
        normalized_filters = _normalize_filters(filters)
        percentiles = percentiles or [0.25, 0.5, 0.75]

        frame = _apply_filters(_df(), normalized_filters)
        output: dict[str, Any] = {}

        for column in columns:
            _validate_column(column)
            series = pd.to_numeric(frame[column], errors="coerce")

            description = series.describe(percentiles=percentiles).to_dict()
            output[column] = {
                key: _json_value(value) for key, value in description.items()
            }
            output[column]["missing"] = int(series.isna().sum())

        return {
            "status": "ok",
            "columns": columns,
            "percentiles": percentiles,
            "filters_applied": normalized_filters,
            "data": output,
            "message": None,
        }

    except Exception as exc:
        return _error(exc)

#@tool
def correlation_analysis(
    columns: Optional[list[str]] = None,
    target: Optional[str] = None,
    method: Literal["pearson", "spearman", "kendall"] = "pearson",
    top_n: int = 20,
) -> dict[str, Any]:
    """Return numeric correlations as a JSON object."""
    try:
        df = _df()
        columns = columns or [
            column for column in df.columns if column in NUMERIC_COLUMNS
        ]

        for column in columns:
            _validate_column(column)

        numeric = df[columns].apply(pd.to_numeric, errors="coerce")
        numeric = numeric.dropna(axis=1, how="all")

        if numeric.shape[1] < 2:
            raise ValueError(
                "At least two columns with numeric observations are required."
            )

        correlation = numeric.corr(method=method)

        if target:
            if target not in correlation.columns:
                raise ValueError(
                    "target must be included in columns and have numeric observations."
                )

            ranked = (
                correlation[target]
                .drop(labels=[target], errors="ignore")
                .dropna()
            )
            ranked = ranked.reindex(
                ranked.abs().sort_values(ascending=False).index
            )

            rows = [
                {"column": key, "correlation": float(value)}
                for key, value in ranked.head(_safe_limit(top_n, 100)).items()
            ]

            return {
                "status": "ok",
                "method": method,
                "target": target,
                "matched_rows": len(rows),
                "returned_rows": len(rows),
                "data": rows,
                "note": "Association only; not evidence of causation.",
                "message": None,
            }

        matrix = _records(correlation.reset_index(names="column"))

        return {
            "status": "ok",
            "method": method,
            "matched_rows": len(matrix),
            "returned_rows": len(matrix),
            "data": matrix,
            "note": "Association only; not evidence of causation.",
            "message": None,
        }

    except Exception as exc:
        return _error(exc)

#@tool
def detect_outliers(
    column: str,
    method: Literal["iqr", "zscore"] = "iqr",
    filters: Optional[list[dict[str, Any]]] = None,
    n: int = 20,
) -> dict[str, Any]:
    """Detect numeric outliers using IQR fences or absolute z-score >= 3."""
    try:
        normalized_filters = _normalize_filters(filters)
        _validate_column(column)

        frame = _apply_filters(_df(), normalized_filters).copy()
        series = pd.to_numeric(frame[column], errors="coerce")

        if method == "iqr":
            q1, q3 = series.quantile([0.25, 0.75])
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            mask = (series < lower) | (series > upper)
            score = (series - series.median()).abs()
            thresholds = {
                "lower": _json_value(lower),
                "upper": _json_value(upper),
            }
        else:
            standard_deviation = series.std()

            if pd.isna(standard_deviation) or standard_deviation == 0:
                zscore = pd.Series(0.0, index=series.index)
            else:
                zscore = (series - series.mean()) / standard_deviation

            mask = zscore.abs() >= 3
            score = zscore.abs()
            thresholds = {"absolute_zscore": 3.0}

        output_columns = [
            existing_column
            for existing_column in ["name", "release_year", "genre", column]
            if existing_column in frame.columns
        ]

        outliers = (
            frame.loc[mask, output_columns]
            .assign(_outlier_score=score.loc[mask])
            .sort_values("_outlier_score", ascending=False)
        )

        rows = _records(outliers.head(_safe_limit(n, 100)))

        return {
            "status": "ok",
            "column": column,
            "method": method,
            "thresholds": thresholds,
            "outlier_count": int(mask.sum()),
            "matched_rows": int(mask.sum()),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": normalized_filters,
            "message": (
                f"No outliers detected in '{column}' using method '{method}'."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def distribution_analysis(
    column: str,
    group_by: Optional[str] = None,
    filters: Optional[list[dict[str, Any]]] = None,
    bins: int = 20,
) -> dict[str, Any]:
    """Return histogram bins for a numeric column, optionally by category."""
    try:
        normalized_filters = _normalize_filters(filters)
        _validate_column(column)

        frame = _apply_filters(_df(), normalized_filters)
        bins = max(2, min(int(bins), 100))

        def histogram(series: pd.Series) -> list[dict[str, Any]]:
            values = pd.to_numeric(series, errors="coerce").dropna()
            if values.empty:
                return []

            counts, edges = np.histogram(values, bins=bins)
            return [
                {
                    "left": float(edges[index]),
                    "right": float(edges[index + 1]),
                    "count": int(counts[index]),
                }
                for index in range(len(counts))
            ]

        if not group_by:
            histogram_data = histogram(frame[column])
            return {
                "status": "ok",
                "column": column,
                "bins": bins,
                "filters_applied": normalized_filters,
                "matched_rows": int(len(frame)),
                "returned_rows": len(histogram_data),
                "data": histogram_data,
                "message": (
                    "No numeric values available for histogram."
                    if not histogram_data
                    else None
                ),
            }

        _validate_column(group_by)

        groups: list[dict[str, Any]] = []
        for key, group in frame.groupby(group_by, dropna=False):
            groups.append({
                "group": _json_value(key),
                "histogram": histogram(group[column]),
            })

        return {
            "status": "ok",
            "column": column,
            "group_by": group_by,
            "bins": bins,
            "filters_applied": normalized_filters,
            "matched_rows": int(len(frame)),
            "returned_rows": len(groups),
            "data": groups,
            "message": (
                f"No groups found for '{group_by}'."
                if not groups
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def analyze_profitability(
    group_by: Optional[str] = None,
    filters: Optional[list[dict[str, Any]]] = None,
    min_budget: Optional[float] = None,
    min_votes: Optional[int] = None,
    metric: str = "roi",
) -> dict[str, Any]:
    """Summarize movie count, financial medians, and profitable percentage."""
    try:
        normalized_filters = _normalize_filters(filters)
        _validate_column(metric)

        extra_filters = normalized_filters.copy()

        if min_budget is not None:
            extra_filters.append({
                "column": "budget",
                "op": ">=",
                "value": min_budget,
            })

        if min_votes is not None:
            extra_filters.append({
                "column": "votes",
                "op": ">=",
                "value": min_votes,
            })

        frame = _apply_filters(_df(), extra_filters)

        if group_by:
            _validate_column(group_by)
            groups = frame.groupby(group_by, dropna=False)
        else:
            groups = [(None, frame)]

        rows: list[dict[str, Any]] = []

        for key, group in groups:
            valid_profit = (
                pd.to_numeric(group["profit"], errors="coerce").dropna()
            )

            row: dict[str, Any] = {
                "movie_count": int(len(group)),
                "median_budget": _json_value(
                    pd.to_numeric(group["budget"], errors="coerce").median()
                ),
                "median_revenue": _json_value(
                    pd.to_numeric(group["revenue"], errors="coerce").median()
                ),
                "median_profit": _json_value(valid_profit.median()),
                f"median_{metric}": _json_value(
                    pd.to_numeric(group[metric], errors="coerce").median()
                ),
                "profitable_pct": _json_value(
                    (valid_profit > 0).mean() * 100
                    if len(valid_profit)
                    else np.nan
                ),
            }

            if group_by:
                row[group_by] = _json_value(key)

            rows.append(row)

        return {
            "status": "ok",
            "group_by": group_by,
            "metric": metric,
            "min_budget": min_budget,
            "min_votes": min_votes,
            "matched_rows": int(len(frame)),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": extra_filters,
            "message": (
                "No records matched the supplied filters."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def find_sleeper_hits(
    max_budget: Optional[float] = None,
    min_roi: Optional[float] = None,
    min_revenue: Optional[float] = None,
    min_votes: Optional[int] = None,
    limit: int = 20,
) -> dict[str, Any]:
    """Find low-budget and/or high-ROI records using caller thresholds."""
    try:
        filters: list[dict[str, Any]] = [
            {"column": "budget", "op": ">", "value": 0},
            {"column": "roi", "op": "not_null"},
        ]

        if max_budget is not None:
            filters.append({
                "column": "budget",
                "op": "<=",
                "value": max_budget,
            })

        if min_roi is not None:
            filters.append({
                "column": "roi",
                "op": ">=",
                "value": min_roi,
            })

        if min_revenue is not None:
            filters.append({
                "column": "revenue",
                "op": ">=",
                "value": min_revenue,
            })

        if min_votes is not None:
            filters.append({
                "column": "votes",
                "op": ">=",
                "value": min_votes,
            })

        frame = _apply_filters(_df(), filters).sort_values(
            "roi", ascending=False
        )

        output_columns = [
            "name", "release_year", "genre", "budget", "revenue",
            "profit", "roi", "votes",
        ]
        output_columns = [
            column for column in output_columns if column in frame.columns
        ]

        rows = _records(
            frame[output_columns].head(_safe_limit(limit, 100))
        )

        return {
            "status": "ok",
            "matched_rows": int(len(frame)),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": filters,
            "message": (
                "No sleeper hits matched the supplied thresholds."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def find_box_office_bombs(
    min_budget: Optional[float] = None,
    max_roi: float = 0.0,
    limit: int = 20,
) -> dict[str, Any]:
    """Find records at or below a caller-selected ROI threshold."""
    try:
        filters: list[dict[str, Any]] = [
            {"column": "roi", "op": "<=", "value": max_roi},
            {"column": "budget", "op": ">", "value": 0},
        ]

        if min_budget is not None:
            filters.append({
                "column": "budget",
                "op": ">=",
                "value": min_budget,
            })

        frame = _apply_filters(_df(), filters).sort_values(
            "profit", ascending=True
        )

        output_columns = [
            "name", "release_year", "genre", "budget", "revenue",
            "profit", "roi",
        ]
        output_columns = [
            column for column in output_columns if column in frame.columns
        ]

        rows = _records(
            frame[output_columns].head(_safe_limit(limit, 100))
        )

        return {
            "status": "ok",
            "matched_rows": int(len(frame)),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": filters,
            "message": (
                "No box-office bombs matched the supplied thresholds."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def _analyze_entity(
    column: str,
    person_or_entity: Optional[str],
    metric: str,
    min_movies: int,
    filters: Optional[list[dict[str, Any]]],
    top_n: int,
) -> pd.DataFrame:
    _validate_column(column)
    _validate_column(metric)

    normalized_filters = _normalize_filters(filters)
    frame = _apply_filters(_df(), normalized_filters)

    if person_or_entity:
        frame = frame.loc[_search_mask(frame[column], person_or_entity)]

    grouped = (
        frame.groupby(column, dropna=False)
        .agg(
            movie_count=("name", "count"),
            metric_median=(metric, "median"),
            metric_mean=(metric, "mean"),
            total_revenue=("revenue", "sum"),
            median_roi=("roi", "median"),
            median_score=("score", "median"),
        )
        .reset_index()
    )

    return grouped.loc[
        grouped["movie_count"] >= max(1, int(min_movies))
    ].sort_values("metric_median", ascending=False).head(
        _safe_limit(top_n, 100)
    )

#@tool
def analyze_talent(
    role: Literal["director", "writer", "star"],
    person: Optional[str] = None,
    metric: str = "revenue",
    min_movies: int = 3,
    filters: Optional[list[dict[str, Any]]] = None,
    top_n: int = 20,
) -> dict[str, Any]:
    """Return descriptive movie-level aggregates by director, writer, or star."""
    try:
        result = _analyze_entity(
            role, person, metric, min_movies, filters, top_n
        )
        rows = _records(result)

        return {
            "status": "ok",
            "entity": role,
            "person": person,
            "metric": metric,
            "min_movies": min_movies,
            "matched_rows": int(len(result)),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": _normalize_filters(filters),
            "message": (
                f"No {role} records matched the supplied criteria."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def analyze_companies(
    metric: str = "revenue",
    min_movies: int = 5,
    filters: Optional[list[dict[str, Any]]] = None,
    top_n: int = 20,
) -> dict[str, Any]:
    """Return company-level descriptive aggregates as a JSON object."""
    try:
        normalized_filters = _normalize_filters(filters)

        result = _analyze_entity(
            column="company",
            person_or_entity=None,
            metric=metric,
            min_movies=min_movies,
            filters=normalized_filters,
            top_n=top_n,
        )

        rows = _records(result)

        return {
            "status": "ok",
            "entity": "company",
            "metric": metric,
            "min_movies": min_movies,
            "matched_rows": int(len(result)),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": normalized_filters,
            "message": (
                "No companies matched the supplied filters. "
                "Check the filter operator and company spelling."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def analyze_genres(
    metric: str = "roi",
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    min_movies: int = 10,
) -> dict[str, Any]:
    """Return genre-level descriptive aggregates with optional year bounds."""
    try:
        filters: list[dict[str, Any]] = []

        if year_from is not None:
            filters.append({
                "column": "release_year",
                "op": ">=",
                "value": year_from,
            })

        if year_to is not None:
            filters.append({
                "column": "release_year",
                "op": "<=",
                "value": year_to,
            })

        result = _analyze_entity(
            column="genre",
            person_or_entity=None,
            metric=metric,
            min_movies=min_movies,
            filters=filters,
            top_n=100,
        )

        rows = _records(result)

        return {
            "status": "ok",
            "entity": "genre",
            "metric": metric,
            "min_movies": min_movies,
            "year_from": year_from,
            "year_to": year_to,
            "matched_rows": int(len(result)),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": filters,
            "message": (
                "No genres matched the supplied criteria."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def analyze_countries(
    metric: str = "revenue",
    min_movies: int = 10,
    top_n: int = 20,
) -> dict[str, Any]:
    """Return country-level descriptive aggregates."""
    try:
        result = _analyze_entity(
            column="country",
            person_or_entity=None,
            metric=metric,
            min_movies=min_movies,
            filters=None,
            top_n=top_n,
        )

        rows = _records(result)

        return {
            "status": "ok",
            "entity": "country",
            "metric": metric,
            "min_movies": min_movies,
            "matched_rows": int(len(result)),
            "returned_rows": len(rows),
            "data": rows,
            "message": (
                "No countries matched the supplied criteria."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def analyze_trends(
    metric: str,
    time_grain: Literal[
        "year", "release_year", "release_month", "release_quarter"
    ] = "release_year",
    group_by: Optional[str] = None,
    filters: Optional[list[dict[str, Any]]] = None,
    statistic: Literal[
        "count", "sum", "mean", "median", "min", "max", "std"
    ] = "median",
) -> dict[str, Any]:
    """Aggregate a metric over time and an optional second dimension."""
    try:
        dimensions = [time_grain]

        if group_by:
            _validate_column(group_by)
            dimensions.append(group_by)

        return aggregate_movies(
            group_by=dimensions,
            metrics=[
                {
                    "column": "name",
                    "agg": "count",
                    "alias": "movie_count",
                },
                {
                    "column": metric,
                    "agg": statistic,
                    "alias": f"{statistic}_{metric}",
                },
            ],
            filters=filters,
            sort_by=time_grain,
            ascending=True,
            limit=1000,
        )

    except Exception as exc:
        return _error(exc)

#@tool
def data_quality_report() -> dict[str, Any]:
    """Report missingness, duplicates, invalid values, and year inconsistencies."""
    try:
        df = _df()

        missing = [
            {
                "column": column,
                "missing": int(df[column].isna().sum()),
                "missing_pct": float(df[column].isna().mean() * 100),
            }
            for column in df.columns
        ]

        invalid_numeric: dict[str, int] = {}
        for column in sorted(NUMERIC_COLUMNS.intersection(df.columns)):
            invalid_numeric[column] = int(
                df[column].notna().sum()
                - pd.to_numeric(df[column], errors="coerce").notna().sum()
            )

        checks: dict[str, Any] = {
            "duplicate_rows": int(df.duplicated().sum()),
            "duplicate_movie_names": (
                int(df["name"].duplicated(keep=False).sum())
                if "name" in df
                else None
            ),
            "zero_or_negative_budget": (
                int(
                    (
                        pd.to_numeric(df.get("budget"), errors="coerce") <= 0
                    ).sum()
                )
                if "budget" in df
                else None
            ),
            "zero_or_negative_revenue": (
                int(
                    (
                        pd.to_numeric(df.get("revenue"), errors="coerce") <= 0
                    ).sum()
                )
                if "revenue" in df
                else None
            ),
        }

        if {"year", "release_year"}.issubset(df.columns):
            year = pd.to_numeric(df["year"], errors="coerce")
            release_year = pd.to_numeric(df["release_year"], errors="coerce")

            checks["year_release_year_mismatch"] = int(
                (
                    year.notna()
                    & release_year.notna()
                    & year.ne(release_year)
                ).sum()
            )

        return {
            "status": "ok",
            "rows": int(len(df)),
            "missingness": missing,
            "invalid_numeric": invalid_numeric,
            "checks": checks,
            "message": None,
        }

    except Exception as exc:
        return _error(exc)

#@tool
def missing_data_analysis(
    columns: Optional[list[str]] = None,
    group_by: Optional[str] = None,
) -> dict[str, Any]:
    """Analyze nulls without treating missing financial values as zero."""
    try:
        df = _df()
        columns = columns or list(df.columns)

        for column in columns:
            _validate_column(column)

        if not group_by:
            data = {
                column: {
                    "missing": int(df[column].isna().sum()),
                    "missing_pct": float(df[column].isna().mean() * 100),
                }
                for column in columns
            }

            return {
                "status": "ok",
                "group_by": None,
                "matched_rows": int(len(df)),
                "returned_rows": len(data),
                "data": data,
                "message": None,
            }

        _validate_column(group_by)

        rows: list[dict[str, Any]] = []
        for key, group in df.groupby(group_by, dropna=False):
            row: dict[str, Any] = {
                group_by: _json_value(key),
                "rows": int(len(group)),
            }

            for column in columns:
                row[f"{column}_missing"] = int(group[column].isna().sum())
                row[f"{column}_missing_pct"] = float(
                    group[column].isna().mean() * 100
                )

            rows.append(row)

        return {
            "status": "ok",
            "group_by": group_by,
            "matched_rows": int(len(df)),
            "returned_rows": len(rows),
            "data": rows,
            "message": None,
        }

    except Exception as exc:
        return _error(exc)

#@tool
def create_chart(
    chart_type: Literal[
        "bar", "line", "scatter", "histogram", "box", "heatmap"
    ],
    x: str,
    y: Optional[str] = None,
    color: Optional[str] = None,
    aggregation: Optional[
        Literal["count", "sum", "mean", "median", "min", "max"]
    ] = None,
    filters: Optional[list[dict[str, Any]]] = None,
    top_n: Optional[int] = None,
) -> dict[str, Any]:
    """Create a PNG chart encoded as base64 and return plotted data."""
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns

        normalized_filters = _normalize_filters(filters)

        _validate_column(x)
        if y:
            _validate_column(y)
        if color:
            _validate_column(color)

        frame = _apply_filters(_df(), normalized_filters).copy()

        if aggregation:
            if not y and aggregation != "count":
                raise ValueError(
                    "y is required for non-count aggregation."
                )

            group_columns = [x] + ([color] if color else [])
            metric = "name" if aggregation == "count" else y

            frame = _aggregate(
                frame,
                group_columns,
                [{
                    "column": metric,
                    "agg": aggregation,
                    "alias": "value",
                }],
            )
            y_plot = "value"
        else:
            y_plot = y

        if top_n:
            sort_column = (
                y_plot
                if y_plot and y_plot in frame.columns
                else x
            )
            frame = frame.sort_values(
                sort_column, ascending=False
            ).head(_safe_limit(top_n, 100))
        elif len(frame) > 5000:
            frame = frame.sample(5000, random_state=42)

        fig, ax = plt.subplots(figsize=(10, 6))

        if chart_type == "bar":
            sns.barplot(data=frame, x=x, y=y_plot, hue=color, ax=ax)
        elif chart_type == "line":
            sns.lineplot(
                data=frame.sort_values(x),
                x=x,
                y=y_plot,
                hue=color,
                marker="o",
                ax=ax,
            )
        elif chart_type == "scatter":
            if not y_plot:
                raise ValueError("scatter requires y.")
            sns.scatterplot(
                data=frame, x=x, y=y_plot, hue=color, ax=ax
            )
        elif chart_type == "histogram":
            sns.histplot(data=frame, x=x, hue=color, ax=ax)
        elif chart_type == "box":
            if not y_plot:
                raise ValueError("box requires y.")
            sns.boxplot(data=frame, x=x, y=y_plot, hue=color, ax=ax)
        else:
            chart_columns = [
                column for column in [x, y, color] if column
            ]
            numeric_frame = frame[chart_columns].apply(
                pd.to_numeric, errors="coerce"
            ).dropna(axis=1, how="all")

            if numeric_frame.shape[1] < 2:
                raise ValueError(
                    "heatmap requires at least two numeric columns."
                )

            correlation = numeric_frame.corr()
            sns.heatmap(
                correlation,
                annot=True,
                cmap="coolwarm",
                center=0,
                ax=ax,
            )

        ax.set_title(
            f"{chart_type.title()}: {x}"
            + (f" vs {y_plot}" if y_plot else "")
        )
        fig.tight_layout()

        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", dpi=150)
        plt.close(fig)

        plotted_data = _records(frame.head(200))

        return {
            "status": "ok",
            "chart_type": chart_type,
            "x": x,
            "y": y,
            "color": color,
            "aggregation": aggregation,
            "mime_type": "image/png",
            "image_base64": base64.b64encode(
                buffer.getvalue()
            ).decode("ascii"),
            "plotted_rows": int(len(frame)),
            "returned_rows": len(plotted_data),
            "data": plotted_data,
            "filters_applied": normalized_filters,
            "message": None,
        }

    except Exception as exc:
        return _error(exc)

#@tool
def answer_movie_analysis(question: str) -> dict[str, Any]:
    """Return a safe routing plan for a natural-language question."""
    try:
        normalized_question = question.casefold()
        routes: list[str] = []

        if any(
            keyword in normalized_question
            for keyword in [
                "find", "show", "movie", "film", "directed", "starring"
            ]
        ):
            routes.append("search_movies")

        if any(
            keyword in normalized_question
            for keyword in [
                "highest", "lowest", "top", "rank", "best", "worst"
            ]
        ):
            routes.append("rank_movies")

        if any(
            keyword in normalized_question
            for keyword in [
                "compare", "versus", " vs ", "by genre", "by country",
                "by company",
            ]
        ):
            routes.append("compare_segments")

        if any(
            keyword in normalized_question
            for keyword in ["trend", "over time", "by year"]
        ):
            routes.append("analyze_trends")

        if any(
            keyword in normalized_question
            for keyword in [
                "correlation", "associated", "relationship"
            ]
        ):
            routes.append("correlation_analysis")

        if any(
            keyword in normalized_question
            for keyword in [
                "summer", "holiday", "awards season", "weekend",
                "month", "quarter",
            ]
        ):
            routes.append("analyze_release_timing")

        if any(
            keyword in normalized_question
            for keyword in [
                "profit", "profitable", "roi", "revenue", "budget"
            ]
        ):
            routes.append("analyze_profitability")

        if not routes:
            routes = [
                "get_dataset_schema",
                "filter_movies",
                "aggregate_movies",
            ]

        return {
            "status": "ok",
            "question": question,
            "recommended_tools": list(dict.fromkeys(routes)),
            "data": [],
            "safety": (
                "Use structured tools only; do not generate or execute "
                "arbitrary dataframe code."
            ),
            "message": None,
        }

    except Exception as exc:
=======
from __future__ import annotations

import base64
import io
import math
import re
from typing import Any, Literal, Optional

import numpy as np
import pandas as pd


URL = "https://raw.githubusercontent.com/stepodo/sas-ram-hackathon/main/data/movie_database.csv"

movies_df: Optional[pd.DataFrame] = pd.read_csv(
    URL,
    dtype={
        "movie_id": "string",
        "name": "string",
        "rating": "string",
        "genre": "string",
        "year": "Int64",
        "released": "string",
        "score": "float64",
        "votes": "Int64",
        "director": "string",
        "writer": "string",
        "star": "string",
        "country": "string",
        "budget": "float64",
        "revenue": "float64",
        "company": "string",
        "runtime": "Int64",
        "release_date": "string",
        "release_month": "Int64",
        "release_year": "Int64",
        "release_quarter": "Int64",
        "release_week": "Int64",
        "release_dayofweek": "Int64",
        "is_weekend_release": "bool",
        "is_summer_release": "bool",
        "is_awards_season": "bool",
        "is_holiday_season": "bool",
        "log_budget": "float64",
        "log_revenue": "float64",
        "profit": "float64",
        "roi": "float64",
        "revenue_budget_ratio": "float64",
        "profit_margin_proxy": "float64",
    },
)


ALLOWED_COLUMNS = {
    "name", "rating", "genre", "year", "released", "score", "votes",
    "director", "writer", "star", "country", "budget", "revenue", "company",
    "runtime", "release_date", "release_month", "release_year",
    "release_quarter", "release_week", "release_dayofweek",
    "is_weekend_release", "is_summer_release", "is_awards_season",
    "is_holiday_season", "log_budget", "log_revenue", "profit", "roi",
    "revenue_budget_ratio", "profit_margin_proxy",
}

NUMERIC_COLUMNS = {
    "year", "score", "votes", "budget", "revenue", "runtime", "release_month",
    "release_year", "release_quarter", "release_week", "release_dayofweek",
    "is_weekend_release", "is_summer_release", "is_awards_season",
    "is_holiday_season", "log_budget", "log_revenue", "profit", "roi",
    "revenue_budget_ratio", "profit_margin_proxy",
}

CATEGORICAL_COLUMNS = {
    "name", "rating", "genre", "released", "director", "writer", "star",
    "country", "company",
}

TIME_DIMENSIONS = {
    "year", "release_year", "release_month", "release_quarter", "release_week",
    "release_dayofweek", "is_weekend_release", "is_summer_release",
    "is_awards_season", "is_holiday_season",
}

AGGREGATIONS = {
    "count", "nunique", "sum", "mean", "median", "min", "max", "std",
}

FILTER_OPERATORS = {
    "=", "eq", "!=", "ne", ">", "gt", ">=", "ge", "<", "lt", "<=", "le",
    "between", "in", "contains", "is_null", "not_null",
}


def set_movies_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    """Bind a live pandas DataFrame to the MCP server."""
    global movies_df

    if not isinstance(df, pd.DataFrame):
        return {
            "status": "error",
            "error_type": "TypeError",
            "message": "df must be a pandas DataFrame.",
            "data": [],
        }

    movies_df = df
    return {
        "status": "ok",
        "message": "DataFrame bound successfully.",
        "rows": int(len(df)),
        "columns": list(df.columns),
        "data": [],
    }


def _df() -> pd.DataFrame:
    if movies_df is None:
        raise RuntimeError(
            "movies_df is not bound. Call set_movies_dataframe(your_dataframe) first."
        )
    return movies_df


def _validate_column(column: str) -> str:
    column = str(column)
    if column not in _df().columns:
        raise ValueError(f"Unknown column: {column}")
    return column


def _json_value(value: Any) -> Any:
    if value is None or value is pd.NA:
        return None

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, (np.floating, float)):
        numeric_value = float(value)
        return numeric_value if math.isfinite(numeric_value) else None

    if isinstance(value, (np.bool_, bool)):
        return bool(value)

    if isinstance(value, (pd.Timestamp, np.datetime64)):
        return pd.Timestamp(value).isoformat()

    return value


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    clean = frame.replace([np.inf, -np.inf], np.nan)
    return [
        {str(key): _json_value(value) for key, value in row.items()}
        for row in clean.to_dict(orient="records")
    ]


def _safe_limit(limit: int, maximum: int = 1000) -> int:
    try:
        limit_int = int(limit)
    except (TypeError, ValueError):
        limit_int = 10
    return max(1, min(limit_int, maximum))


def _normalize_filters(
    filters: Optional[list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Normalize filter objects and accept both 'op' and 'operator'."""
    if not filters:
        return []

    if not isinstance(filters, list):
        raise ValueError("filters must be a list of objects.")

    normalized: list[dict[str, Any]] = []
    allowed_keys = {"column", "op", "operator", "value"}

    for index, item in enumerate(filters):
        if not isinstance(item, dict):
            raise ValueError(f"filters[{index}] must be an object.")

        unknown_keys = set(item.keys()) - allowed_keys
        if unknown_keys:
            raise ValueError(
                f"filters[{index}] contains unsupported key(s): "
                f"{sorted(unknown_keys)}. Allowed keys: {sorted(allowed_keys)}."
            )

        column = item.get("column")
        if not column:
            raise ValueError(f"filters[{index}] must define 'column'.")

        operator = item.get("op", item.get("operator"))
        if operator is None:
            raise ValueError(
                f"filters[{index}] must define 'op' or 'operator'."
            )

        operator = str(operator).lower().strip()
        if operator not in FILTER_OPERATORS:
            raise ValueError(
                f"filters[{index}] has unsupported operator: {operator}. "
                f"Supported operators: {sorted(FILTER_OPERATORS)}."
            )

        normalized.append({
            "column": str(column),
            "op": operator,
            "value": item.get("value"),
        })

    return normalized


def _apply_filters(
    frame: pd.DataFrame,
    filters: Optional[list[dict[str, Any]]],
) -> pd.DataFrame:
    filters = _normalize_filters(filters)

    if not filters:
        return frame.copy()

    result = frame.copy()

    for item in filters:
        column = _validate_column(item["column"])
        operator = item["op"]
        value = item["value"]
        series = result[column]

        if operator in {"=", "eq"}:
            mask = series.eq(value)
        elif operator in {"!=", "ne"}:
            mask = series.ne(value)
        elif operator in {">", "gt"}:
            mask = pd.to_numeric(series, errors="coerce") > float(value)
        elif operator in {">=", "ge"}:
            mask = pd.to_numeric(series, errors="coerce") >= float(value)
        elif operator in {"<", "lt"}:
            mask = pd.to_numeric(series, errors="coerce") < float(value)
        elif operator in {"<=", "le"}:
            mask = pd.to_numeric(series, errors="coerce") <= float(value)
        elif operator == "between":
            if not isinstance(value, (list, tuple)) or len(value) != 2:
                raise ValueError("between requires value=[lower, upper].")
            numeric = pd.to_numeric(series, errors="coerce")
            mask = numeric.between(
                float(value[0]), float(value[1]), inclusive="both"
            )
        elif operator == "in":
            if not isinstance(value, list):
                raise ValueError("in requires a list value.")
            mask = series.isin(value)
        elif operator == "contains":
            mask = series.astype("string").str.contains(
                re.escape(str(value)), case=False, na=False, regex=True
            )
        elif operator == "is_null":
            mask = series.isna()
        elif operator == "not_null":
            mask = series.notna()
        else:
            raise ValueError(f"Unsupported operator: {operator}")

        result = result.loc[mask.fillna(False)]

    return result


def _aggregate(
    frame: pd.DataFrame,
    group_by: list[str],
    metrics: list[dict[str, str]],
) -> pd.DataFrame:
    for column in group_by:
        _validate_column(column)

    if not metrics:
        raise ValueError("At least one metric is required.")

    named_aggs: dict[str, pd.NamedAgg] = {}

    for metric in metrics:
        column = _validate_column(metric["column"])
        aggregation = str(metric["agg"]).lower().strip()

        if aggregation not in AGGREGATIONS:
            raise ValueError(f"Unsupported aggregation: {aggregation}")

        alias = metric.get("alias") or f"{column}_{aggregation}"
        named_aggs[alias] = pd.NamedAgg(column=column, aggfunc=aggregation)

    if group_by:
        return (
            frame.groupby(group_by, dropna=False)
            .agg(**named_aggs)
            .reset_index()
        )

    values = {
        alias: getattr(frame[spec.column], spec.aggfunc)()
        for alias, spec in named_aggs.items()
    }
    return pd.DataFrame([values])


def _search_mask(series: pd.Series, text: Optional[str]) -> pd.Series:
    if not text:
        return pd.Series(True, index=series.index)

    return series.astype("string").str.contains(
        re.escape(str(text)), case=False, na=False
    )


def _ok(
    data: list[dict[str, Any]],
    message: Optional[str] = None,
    **metadata: Any,
) -> dict[str, Any]:
    return {
        "status": "ok",
        "matched_rows": len(data),
        "returned_rows": len(data),
        "data": data,
        "message": message,
        **metadata,
    }


def _error(exc: Exception) -> dict[str, Any]:
    return {
        "status": "error",
        "error_type": type(exc).__name__,
        "message": str(exc),
        "data": [],
    }

#@tool
def get_dataset_schema(sample_rows: int = 5) -> dict[str, Any]:
    """Return shape, data types, null rates, cardinality, ranges, and samples."""
    try:
        df = _df()
        columns: list[dict[str, Any]] = []

        for column in df.columns:
            series = df[column]
            numeric = pd.to_numeric(series, errors="coerce")

            item: dict[str, Any] = {
                "name": column,
                "dtype": str(series.dtype),
                "non_null": int(series.notna().sum()),
                "missing": int(series.isna().sum()),
                "missing_pct": float(series.isna().mean() * 100),
                "unique": int(series.nunique(dropna=True)),
            }

            if numeric.notna().any() and (
                column in NUMERIC_COLUMNS
                or pd.api.types.is_numeric_dtype(series)
            ):
                item["min"] = _json_value(numeric.min())
                item["max"] = _json_value(numeric.max())

            columns.append(item)

        sample = _records(df.head(_safe_limit(sample_rows, 20)))

        return {
            "status": "ok",
            "rows": int(len(df)),
            "columns_count": int(len(df.columns)),
            "columns": columns,
            "sample": sample,
            "message": None,
        }

    except Exception as exc:
        return _error(exc)

#@tool
def search_movies(
    name: Optional[str] = None,
    genre: Optional[str] = None,
    director: Optional[str] = None,
    writer: Optional[str] = None,
    star: Optional[str] = None,
    company: Optional[str] = None,
    country: Optional[str] = None,
    rating: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    limit: int = 20,
) -> dict[str, Any]:
    """Search movies using case-insensitive partial text and year bounds."""
    try:
        df = _df()
        mask = pd.Series(True, index=df.index)

        text_filters = {
            "name": name,
            "genre": genre,
            "director": director,
            "writer": writer,
            "star": star,
            "company": company,
            "country": country,
            "rating": rating,
        }

        for column, text in text_filters.items():
            if text is not None:
                mask &= _search_mask(df[column], text)

        year_column = "release_year" if "release_year" in df.columns else "year"
        years = pd.to_numeric(df[year_column], errors="coerce")

        if year_from is not None:
            mask &= years >= year_from
        if year_to is not None:
            mask &= years <= year_to

        matched = df.loc[mask]
        rows = _records(matched.head(_safe_limit(limit)))

        return {
            "status": "ok",
            "matched_rows": int(mask.sum()),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": {
                **{key: value for key, value in text_filters.items() if value is not None},
                "year_from": year_from,
                "year_to": year_to,
                "limit": limit,
            },
            "message": (
                "No movies matched the supplied criteria."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def get_movie(name: str, limit: int = 10) -> dict[str, Any]:
    """Return exact matches first, then case-insensitive partial matches."""
    try:
        df = _df()
        names = df["name"].astype("string")

        exact = df.loc[names.str.casefold() == name.casefold()]
        partial = df.loc[
            names.str.contains(re.escape(name), case=False, na=False)
        ]

        matched = pd.concat([exact, partial]).loc[
            lambda frame: ~frame.index.duplicated(keep="first")
        ]

        rows = _records(matched.head(_safe_limit(limit, 50)))

        return {
            "status": "ok",
            "query": name,
            "matched_rows": int(len(matched)),
            "returned_rows": len(rows),
            "data": rows,
            "message": (
                f"No movie matched '{name}'."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def filter_movies(
    filters: Optional[list[dict[str, Any]]] = None,
    columns: Optional[list[str]] = None,
    sort_by: Optional[str] = None,
    ascending: bool = False,
    limit: int = 100,
) -> dict[str, Any]:
    """Filter using structured operators and return a JSON object."""
    try:
        normalized_filters = _normalize_filters(filters)
        result = _apply_filters(_df(), normalized_filters)

        if sort_by:
            _validate_column(sort_by)
            result = result.sort_values(
                sort_by, ascending=ascending, na_position="last"
            )

        if columns:
            for column in columns:
                _validate_column(column)
            result = result[columns]

        rows = _records(result.head(_safe_limit(limit)))

        return {
            "status": "ok",
            "matched_rows": int(len(result)),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": normalized_filters,
            "columns_selected": columns,
            "sort_by": sort_by,
            "ascending": ascending,
            "limit": limit,
            "message": (
                "No rows matched the supplied filters."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def rank_movies(
    metric: str,
    n: int = 10,
    ascending: bool = False,
    filters: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    """Rank movies by a numeric metric after optional filtering."""
    try:
        normalized_filters = _normalize_filters(filters)
        _validate_column(metric)

        result = _apply_filters(_df(), normalized_filters).copy()
        result[metric] = pd.to_numeric(result[metric], errors="coerce")

        output_columns = [
            column
            for column in ["name", "release_year", "genre", metric]
            if column in result.columns
        ]

        ranked = (
            result.dropna(subset=[metric])
            .sort_values(metric, ascending=ascending)[output_columns]
            .head(_safe_limit(n, 100))
        )

        rows = _records(ranked)

        return {
            "status": "ok",
            "metric": metric,
            "ascending": ascending,
            "matched_rows": int(len(result.dropna(subset=[metric]))),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": normalized_filters,
            "message": (
                f"No non-null values found for metric '{metric}'."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def aggregate_movies(
    group_by: list[str],
    metrics: list[dict[str, str]],
    filters: Optional[list[dict[str, Any]]] = None,
    sort_by: Optional[str] = None,
    ascending: bool = False,
    limit: int = 50,
) -> dict[str, Any]:
    """Perform safe group-by aggregations and return a JSON object."""
    try:
        normalized_filters = _normalize_filters(filters)
        result = _aggregate(
            _apply_filters(_df(), normalized_filters),
            group_by,
            metrics,
        )

        if sort_by:
            if sort_by not in result.columns:
                raise ValueError(
                    f"Unknown aggregated output column: {sort_by}"
                )
            result = result.sort_values(
                sort_by, ascending=ascending, na_position="last"
            )

        rows = _records(result.head(_safe_limit(limit, 500)))

        return {
            "status": "ok",
            "group_by": group_by,
            "metrics": metrics,
            "matched_rows": int(len(result)),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": normalized_filters,
            "sort_by": sort_by,
            "ascending": ascending,
            "message": (
                "No aggregate rows were produced."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def compare_segments(
    dimension: str,
    metrics: Optional[list[str]] = None,
    filters: Optional[list[dict[str, Any]]] = None,
    top_n: int = 20,
) -> dict[str, Any]:
    """Compare categories using count, median, and mean metrics."""
    try:
        normalized_filters = _normalize_filters(filters)
        _validate_column(dimension)

        metrics = metrics or ["revenue", "profit", "roi", "score"]

        specs: list[dict[str, str]] = [
            {"column": "name", "agg": "count", "alias": "movie_count"}
        ]

        for metric in metrics:
            _validate_column(metric)
            specs.extend([
                {
                    "column": metric,
                    "agg": "median",
                    "alias": f"median_{metric}",
                },
                {
                    "column": metric,
                    "agg": "mean",
                    "alias": f"mean_{metric}",
                },
            ])

        result = _aggregate(
            _apply_filters(_df(), normalized_filters),
            [dimension],
            specs,
        )

        result = result.sort_values(
            "movie_count", ascending=False
        ).head(_safe_limit(top_n, 100))

        rows = _records(result)

        return {
            "status": "ok",
            "dimension": dimension,
            "metrics": metrics,
            "matched_rows": int(len(result)),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": normalized_filters,
            "message": (
                f"No segments found for dimension '{dimension}'."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def analyze_release_timing(
    metric: str = "revenue",
    group_by: str = "release_month",
    statistic: Literal[
        "count", "sum", "mean", "median", "min", "max", "std"
    ] = "median",
    filters: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    """Analyze a metric by an engineered release-calendar dimension."""
    try:
        if group_by not in TIME_DIMENSIONS:
            raise ValueError(
                f"group_by must be one of {sorted(TIME_DIMENSIONS)}."
            )

        _validate_column(metric)

        return aggregate_movies(
            group_by=[group_by],
            metrics=[
                {
                    "column": "name",
                    "agg": "count",
                    "alias": "movie_count",
                },
                {
                    "column": metric,
                    "agg": statistic,
                    "alias": f"{statistic}_{metric}",
                },
            ],
            filters=filters,
            sort_by=group_by,
            ascending=True,
            limit=100,
        )

    except Exception as exc:
        return _error(exc)

#@tool
def describe_metrics(
    columns: list[str],
    filters: Optional[list[dict[str, Any]]] = None,
    percentiles: Optional[list[float]] = None,
) -> dict[str, Any]:
    """Return descriptive statistics for requested numeric columns."""
    try:
        normalized_filters = _normalize_filters(filters)
        percentiles = percentiles or [0.25, 0.5, 0.75]

        frame = _apply_filters(_df(), normalized_filters)
        output: dict[str, Any] = {}

        for column in columns:
            _validate_column(column)
            series = pd.to_numeric(frame[column], errors="coerce")

            description = series.describe(percentiles=percentiles).to_dict()
            output[column] = {
                key: _json_value(value) for key, value in description.items()
            }
            output[column]["missing"] = int(series.isna().sum())

        return {
            "status": "ok",
            "columns": columns,
            "percentiles": percentiles,
            "filters_applied": normalized_filters,
            "data": output,
            "message": None,
        }

    except Exception as exc:
        return _error(exc)

#@tool
def correlation_analysis(
    columns: Optional[list[str]] = None,
    target: Optional[str] = None,
    method: Literal["pearson", "spearman", "kendall"] = "pearson",
    top_n: int = 20,
) -> dict[str, Any]:
    """Return numeric correlations as a JSON object."""
    try:
        df = _df()
        columns = columns or [
            column for column in df.columns if column in NUMERIC_COLUMNS
        ]

        for column in columns:
            _validate_column(column)

        numeric = df[columns].apply(pd.to_numeric, errors="coerce")
        numeric = numeric.dropna(axis=1, how="all")

        if numeric.shape[1] < 2:
            raise ValueError(
                "At least two columns with numeric observations are required."
            )

        correlation = numeric.corr(method=method)

        if target:
            if target not in correlation.columns:
                raise ValueError(
                    "target must be included in columns and have numeric observations."
                )

            ranked = (
                correlation[target]
                .drop(labels=[target], errors="ignore")
                .dropna()
            )
            ranked = ranked.reindex(
                ranked.abs().sort_values(ascending=False).index
            )

            rows = [
                {"column": key, "correlation": float(value)}
                for key, value in ranked.head(_safe_limit(top_n, 100)).items()
            ]

            return {
                "status": "ok",
                "method": method,
                "target": target,
                "matched_rows": len(rows),
                "returned_rows": len(rows),
                "data": rows,
                "note": "Association only; not evidence of causation.",
                "message": None,
            }

        matrix = _records(correlation.reset_index(names="column"))

        return {
            "status": "ok",
            "method": method,
            "matched_rows": len(matrix),
            "returned_rows": len(matrix),
            "data": matrix,
            "note": "Association only; not evidence of causation.",
            "message": None,
        }

    except Exception as exc:
        return _error(exc)

#@tool
def detect_outliers(
    column: str,
    method: Literal["iqr", "zscore"] = "iqr",
    filters: Optional[list[dict[str, Any]]] = None,
    n: int = 20,
) -> dict[str, Any]:
    """Detect numeric outliers using IQR fences or absolute z-score >= 3."""
    try:
        normalized_filters = _normalize_filters(filters)
        _validate_column(column)

        frame = _apply_filters(_df(), normalized_filters).copy()
        series = pd.to_numeric(frame[column], errors="coerce")

        if method == "iqr":
            q1, q3 = series.quantile([0.25, 0.75])
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            mask = (series < lower) | (series > upper)
            score = (series - series.median()).abs()
            thresholds = {
                "lower": _json_value(lower),
                "upper": _json_value(upper),
            }
        else:
            standard_deviation = series.std()

            if pd.isna(standard_deviation) or standard_deviation == 0:
                zscore = pd.Series(0.0, index=series.index)
            else:
                zscore = (series - series.mean()) / standard_deviation

            mask = zscore.abs() >= 3
            score = zscore.abs()
            thresholds = {"absolute_zscore": 3.0}

        output_columns = [
            existing_column
            for existing_column in ["name", "release_year", "genre", column]
            if existing_column in frame.columns
        ]

        outliers = (
            frame.loc[mask, output_columns]
            .assign(_outlier_score=score.loc[mask])
            .sort_values("_outlier_score", ascending=False)
        )

        rows = _records(outliers.head(_safe_limit(n, 100)))

        return {
            "status": "ok",
            "column": column,
            "method": method,
            "thresholds": thresholds,
            "outlier_count": int(mask.sum()),
            "matched_rows": int(mask.sum()),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": normalized_filters,
            "message": (
                f"No outliers detected in '{column}' using method '{method}'."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def distribution_analysis(
    column: str,
    group_by: Optional[str] = None,
    filters: Optional[list[dict[str, Any]]] = None,
    bins: int = 20,
) -> dict[str, Any]:
    """Return histogram bins for a numeric column, optionally by category."""
    try:
        normalized_filters = _normalize_filters(filters)
        _validate_column(column)

        frame = _apply_filters(_df(), normalized_filters)
        bins = max(2, min(int(bins), 100))

        def histogram(series: pd.Series) -> list[dict[str, Any]]:
            values = pd.to_numeric(series, errors="coerce").dropna()
            if values.empty:
                return []

            counts, edges = np.histogram(values, bins=bins)
            return [
                {
                    "left": float(edges[index]),
                    "right": float(edges[index + 1]),
                    "count": int(counts[index]),
                }
                for index in range(len(counts))
            ]

        if not group_by:
            histogram_data = histogram(frame[column])
            return {
                "status": "ok",
                "column": column,
                "bins": bins,
                "filters_applied": normalized_filters,
                "matched_rows": int(len(frame)),
                "returned_rows": len(histogram_data),
                "data": histogram_data,
                "message": (
                    "No numeric values available for histogram."
                    if not histogram_data
                    else None
                ),
            }

        _validate_column(group_by)

        groups: list[dict[str, Any]] = []
        for key, group in frame.groupby(group_by, dropna=False):
            groups.append({
                "group": _json_value(key),
                "histogram": histogram(group[column]),
            })

        return {
            "status": "ok",
            "column": column,
            "group_by": group_by,
            "bins": bins,
            "filters_applied": normalized_filters,
            "matched_rows": int(len(frame)),
            "returned_rows": len(groups),
            "data": groups,
            "message": (
                f"No groups found for '{group_by}'."
                if not groups
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def analyze_profitability(
    group_by: Optional[str] = None,
    filters: Optional[list[dict[str, Any]]] = None,
    min_budget: Optional[float] = None,
    min_votes: Optional[int] = None,
    metric: str = "roi",
) -> dict[str, Any]:
    """Summarize movie count, financial medians, and profitable percentage."""
    try:
        normalized_filters = _normalize_filters(filters)
        _validate_column(metric)

        extra_filters = normalized_filters.copy()

        if min_budget is not None:
            extra_filters.append({
                "column": "budget",
                "op": ">=",
                "value": min_budget,
            })

        if min_votes is not None:
            extra_filters.append({
                "column": "votes",
                "op": ">=",
                "value": min_votes,
            })

        frame = _apply_filters(_df(), extra_filters)

        if group_by:
            _validate_column(group_by)
            groups = frame.groupby(group_by, dropna=False)
        else:
            groups = [(None, frame)]

        rows: list[dict[str, Any]] = []

        for key, group in groups:
            valid_profit = (
                pd.to_numeric(group["profit"], errors="coerce").dropna()
            )

            row: dict[str, Any] = {
                "movie_count": int(len(group)),
                "median_budget": _json_value(
                    pd.to_numeric(group["budget"], errors="coerce").median()
                ),
                "median_revenue": _json_value(
                    pd.to_numeric(group["revenue"], errors="coerce").median()
                ),
                "median_profit": _json_value(valid_profit.median()),
                f"median_{metric}": _json_value(
                    pd.to_numeric(group[metric], errors="coerce").median()
                ),
                "profitable_pct": _json_value(
                    (valid_profit > 0).mean() * 100
                    if len(valid_profit)
                    else np.nan
                ),
            }

            if group_by:
                row[group_by] = _json_value(key)

            rows.append(row)

        return {
            "status": "ok",
            "group_by": group_by,
            "metric": metric,
            "min_budget": min_budget,
            "min_votes": min_votes,
            "matched_rows": int(len(frame)),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": extra_filters,
            "message": (
                "No records matched the supplied filters."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def find_sleeper_hits(
    max_budget: Optional[float] = None,
    min_roi: Optional[float] = None,
    min_revenue: Optional[float] = None,
    min_votes: Optional[int] = None,
    limit: int = 20,
) -> dict[str, Any]:
    """Find low-budget and/or high-ROI records using caller thresholds."""
    try:
        filters: list[dict[str, Any]] = [
            {"column": "budget", "op": ">", "value": 0},
            {"column": "roi", "op": "not_null"},
        ]

        if max_budget is not None:
            filters.append({
                "column": "budget",
                "op": "<=",
                "value": max_budget,
            })

        if min_roi is not None:
            filters.append({
                "column": "roi",
                "op": ">=",
                "value": min_roi,
            })

        if min_revenue is not None:
            filters.append({
                "column": "revenue",
                "op": ">=",
                "value": min_revenue,
            })

        if min_votes is not None:
            filters.append({
                "column": "votes",
                "op": ">=",
                "value": min_votes,
            })

        frame = _apply_filters(_df(), filters).sort_values(
            "roi", ascending=False
        )

        output_columns = [
            "name", "release_year", "genre", "budget", "revenue",
            "profit", "roi", "votes",
        ]
        output_columns = [
            column for column in output_columns if column in frame.columns
        ]

        rows = _records(
            frame[output_columns].head(_safe_limit(limit, 100))
        )

        return {
            "status": "ok",
            "matched_rows": int(len(frame)),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": filters,
            "message": (
                "No sleeper hits matched the supplied thresholds."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def find_box_office_bombs(
    min_budget: Optional[float] = None,
    max_roi: float = 0.0,
    limit: int = 20,
) -> dict[str, Any]:
    """Find records at or below a caller-selected ROI threshold."""
    try:
        filters: list[dict[str, Any]] = [
            {"column": "roi", "op": "<=", "value": max_roi},
            {"column": "budget", "op": ">", "value": 0},
        ]

        if min_budget is not None:
            filters.append({
                "column": "budget",
                "op": ">=",
                "value": min_budget,
            })

        frame = _apply_filters(_df(), filters).sort_values(
            "profit", ascending=True
        )

        output_columns = [
            "name", "release_year", "genre", "budget", "revenue",
            "profit", "roi",
        ]
        output_columns = [
            column for column in output_columns if column in frame.columns
        ]

        rows = _records(
            frame[output_columns].head(_safe_limit(limit, 100))
        )

        return {
            "status": "ok",
            "matched_rows": int(len(frame)),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": filters,
            "message": (
                "No box-office bombs matched the supplied thresholds."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)


def _analyze_entity(
    column: str,
    person_or_entity: Optional[str],
    metric: str,
    min_movies: int,
    filters: Optional[list[dict[str, Any]]],
    top_n: int,
) -> pd.DataFrame:
    _validate_column(column)
    _validate_column(metric)

    normalized_filters = _normalize_filters(filters)
    frame = _apply_filters(_df(), normalized_filters)

    if person_or_entity:
        frame = frame.loc[_search_mask(frame[column], person_or_entity)]

    grouped = (
        frame.groupby(column, dropna=False)
        .agg(
            movie_count=("name", "count"),
            metric_median=(metric, "median"),
            metric_mean=(metric, "mean"),
            total_revenue=("revenue", "sum"),
            median_roi=("roi", "median"),
            median_score=("score", "median"),
        )
        .reset_index()
    )

    return grouped.loc[
        grouped["movie_count"] >= max(1, int(min_movies))
    ].sort_values("metric_median", ascending=False).head(
        _safe_limit(top_n, 100)
    )

#@tool
def analyze_talent(
    role: Literal["director", "writer", "star"],
    person: Optional[str] = None,
    metric: str = "revenue",
    min_movies: int = 3,
    filters: Optional[list[dict[str, Any]]] = None,
    top_n: int = 20,
) -> dict[str, Any]:
    """Return descriptive movie-level aggregates by director, writer, or star."""
    try:
        result = _analyze_entity(
            role, person, metric, min_movies, filters, top_n
        )
        rows = _records(result)

        return {
            "status": "ok",
            "entity": role,
            "person": person,
            "metric": metric,
            "min_movies": min_movies,
            "matched_rows": int(len(result)),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": _normalize_filters(filters),
            "message": (
                f"No {role} records matched the supplied criteria."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def analyze_companies(
    metric: str = "revenue",
    min_movies: int = 5,
    filters: Optional[list[dict[str, Any]]] = None,
    top_n: int = 20,
) -> dict[str, Any]:
    """Return company-level descriptive aggregates as a JSON object."""
    try:
        normalized_filters = _normalize_filters(filters)

        result = _analyze_entity(
            column="company",
            person_or_entity=None,
            metric=metric,
            min_movies=min_movies,
            filters=normalized_filters,
            top_n=top_n,
        )

        rows = _records(result)

        return {
            "status": "ok",
            "entity": "company",
            "metric": metric,
            "min_movies": min_movies,
            "matched_rows": int(len(result)),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": normalized_filters,
            "message": (
                "No companies matched the supplied filters. "
                "Check the filter operator and company spelling."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def analyze_genres(
    metric: str = "roi",
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    min_movies: int = 10,
) -> dict[str, Any]:
    """Return genre-level descriptive aggregates with optional year bounds."""
    try:
        filters: list[dict[str, Any]] = []

        if year_from is not None:
            filters.append({
                "column": "release_year",
                "op": ">=",
                "value": year_from,
            })

        if year_to is not None:
            filters.append({
                "column": "release_year",
                "op": "<=",
                "value": year_to,
            })

        result = _analyze_entity(
            column="genre",
            person_or_entity=None,
            metric=metric,
            min_movies=min_movies,
            filters=filters,
            top_n=100,
        )

        rows = _records(result)

        return {
            "status": "ok",
            "entity": "genre",
            "metric": metric,
            "min_movies": min_movies,
            "year_from": year_from,
            "year_to": year_to,
            "matched_rows": int(len(result)),
            "returned_rows": len(rows),
            "data": rows,
            "filters_applied": filters,
            "message": (
                "No genres matched the supplied criteria."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def analyze_countries(
    metric: str = "revenue",
    min_movies: int = 10,
    top_n: int = 20,
) -> dict[str, Any]:
    """Return country-level descriptive aggregates."""
    try:
        result = _analyze_entity(
            column="country",
            person_or_entity=None,
            metric=metric,
            min_movies=min_movies,
            filters=None,
            top_n=top_n,
        )

        rows = _records(result)

        return {
            "status": "ok",
            "entity": "country",
            "metric": metric,
            "min_movies": min_movies,
            "matched_rows": int(len(result)),
            "returned_rows": len(rows),
            "data": rows,
            "message": (
                "No countries matched the supplied criteria."
                if not rows
                else None
            ),
        }

    except Exception as exc:
        return _error(exc)

#@tool
def analyze_trends(
    metric: str,
    time_grain: Literal[
        "year", "release_year", "release_month", "release_quarter"
    ] = "release_year",
    group_by: Optional[str] = None,
    filters: Optional[list[dict[str, Any]]] = None,
    statistic: Literal[
        "count", "sum", "mean", "median", "min", "max", "std"
    ] = "median",
) -> dict[str, Any]:
    """Aggregate a metric over time and an optional second dimension."""
    try:
        dimensions = [time_grain]

        if group_by:
            _validate_column(group_by)
            dimensions.append(group_by)

        return aggregate_movies(
            group_by=dimensions,
            metrics=[
                {
                    "column": "name",
                    "agg": "count",
                    "alias": "movie_count",
                },
                {
                    "column": metric,
                    "agg": statistic,
                    "alias": f"{statistic}_{metric}",
                },
            ],
            filters=filters,
            sort_by=time_grain,
            ascending=True,
            limit=1000,
        )

    except Exception as exc:
        return _error(exc)

#@tool
def data_quality_report() -> dict[str, Any]:
    """Report missingness, duplicates, invalid values, and year inconsistencies."""
    try:
        df = _df()

        missing = [
            {
                "column": column,
                "missing": int(df[column].isna().sum()),
                "missing_pct": float(df[column].isna().mean() * 100),
            }
            for column in df.columns
        ]

        invalid_numeric: dict[str, int] = {}
        for column in sorted(NUMERIC_COLUMNS.intersection(df.columns)):
            invalid_numeric[column] = int(
                df[column].notna().sum()
                - pd.to_numeric(df[column], errors="coerce").notna().sum()
            )

        checks: dict[str, Any] = {
            "duplicate_rows": int(df.duplicated().sum()),
            "duplicate_movie_names": (
                int(df["name"].duplicated(keep=False).sum())
                if "name" in df
                else None
            ),
            "zero_or_negative_budget": (
                int(
                    (
                        pd.to_numeric(df.get("budget"), errors="coerce") <= 0
                    ).sum()
                )
                if "budget" in df
                else None
            ),
            "zero_or_negative_revenue": (
                int(
                    (
                        pd.to_numeric(df.get("revenue"), errors="coerce") <= 0
                    ).sum()
                )
                if "revenue" in df
                else None
            ),
        }

        if {"year", "release_year"}.issubset(df.columns):
            year = pd.to_numeric(df["year"], errors="coerce")
            release_year = pd.to_numeric(df["release_year"], errors="coerce")

            checks["year_release_year_mismatch"] = int(
                (
                    year.notna()
                    & release_year.notna()
                    & year.ne(release_year)
                ).sum()
            )

        return {
            "status": "ok",
            "rows": int(len(df)),
            "missingness": missing,
            "invalid_numeric": invalid_numeric,
            "checks": checks,
            "message": None,
        }

    except Exception as exc:
        return _error(exc)

#@tool
def missing_data_analysis(
    columns: Optional[list[str]] = None,
    group_by: Optional[str] = None,
) -> dict[str, Any]:
    """Analyze nulls without treating missing financial values as zero."""
    try:
        df = _df()
        columns = columns or list(df.columns)

        for column in columns:
            _validate_column(column)

        if not group_by:
            data = {
                column: {
                    "missing": int(df[column].isna().sum()),
                    "missing_pct": float(df[column].isna().mean() * 100),
                }
                for column in columns
            }

            return {
                "status": "ok",
                "group_by": None,
                "matched_rows": int(len(df)),
                "returned_rows": len(data),
                "data": data,
                "message": None,
            }

        _validate_column(group_by)

        rows: list[dict[str, Any]] = []
        for key, group in df.groupby(group_by, dropna=False):
            row: dict[str, Any] = {
                group_by: _json_value(key),
                "rows": int(len(group)),
            }

            for column in columns:
                row[f"{column}_missing"] = int(group[column].isna().sum())
                row[f"{column}_missing_pct"] = float(
                    group[column].isna().mean() * 100
                )

            rows.append(row)

        return {
            "status": "ok",
            "group_by": group_by,
            "matched_rows": int(len(df)),
            "returned_rows": len(rows),
            "data": rows,
            "message": None,
        }

    except Exception as exc:
        return _error(exc)

#@tool
def create_chart(
    chart_type: Literal[
        "bar", "line", "scatter", "histogram", "box", "heatmap"
    ],
    x: str,
    y: Optional[str] = None,
    color: Optional[str] = None,
    aggregation: Optional[
        Literal["count", "sum", "mean", "median", "min", "max"]
    ] = None,
    filters: Optional[list[dict[str, Any]]] = None,
    top_n: Optional[int] = None,
) -> dict[str, Any]:
    """Create a PNG chart encoded as base64 and return plotted data."""
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns

        normalized_filters = _normalize_filters(filters)

        _validate_column(x)
        if y:
            _validate_column(y)
        if color:
            _validate_column(color)

        frame = _apply_filters(_df(), normalized_filters).copy()

        if aggregation:
            if not y and aggregation != "count":
                raise ValueError(
                    "y is required for non-count aggregation."
                )

            group_columns = [x] + ([color] if color else [])
            metric = "name" if aggregation == "count" else y

            frame = _aggregate(
                frame,
                group_columns,
                [{
                    "column": metric,
                    "agg": aggregation,
                    "alias": "value",
                }],
            )
            y_plot = "value"
        else:
            y_plot = y

        if top_n:
            sort_column = (
                y_plot
                if y_plot and y_plot in frame.columns
                else x
            )
            frame = frame.sort_values(
                sort_column, ascending=False
            ).head(_safe_limit(top_n, 100))
        elif len(frame) > 5000:
            frame = frame.sample(5000, random_state=42)

        fig, ax = plt.subplots(figsize=(10, 6))

        if chart_type == "bar":
            sns.barplot(data=frame, x=x, y=y_plot, hue=color, ax=ax)
        elif chart_type == "line":
            sns.lineplot(
                data=frame.sort_values(x),
                x=x,
                y=y_plot,
                hue=color,
                marker="o",
                ax=ax,
            )
        elif chart_type == "scatter":
            if not y_plot:
                raise ValueError("scatter requires y.")
            sns.scatterplot(
                data=frame, x=x, y=y_plot, hue=color, ax=ax
            )
        elif chart_type == "histogram":
            sns.histplot(data=frame, x=x, hue=color, ax=ax)
        elif chart_type == "box":
            if not y_plot:
                raise ValueError("box requires y.")
            sns.boxplot(data=frame, x=x, y=y_plot, hue=color, ax=ax)
        else:
            chart_columns = [
                column for column in [x, y, color] if column
            ]
            numeric_frame = frame[chart_columns].apply(
                pd.to_numeric, errors="coerce"
            ).dropna(axis=1, how="all")

            if numeric_frame.shape[1] < 2:
                raise ValueError(
                    "heatmap requires at least two numeric columns."
                )

            correlation = numeric_frame.corr()
            sns.heatmap(
                correlation,
                annot=True,
                cmap="coolwarm",
                center=0,
                ax=ax,
            )

        ax.set_title(
            f"{chart_type.title()}: {x}"
            + (f" vs {y_plot}" if y_plot else "")
        )
        fig.tight_layout()

        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", dpi=150)
        plt.close(fig)

        plotted_data = _records(frame.head(200))

        return {
            "status": "ok",
            "chart_type": chart_type,
            "x": x,
            "y": y,
            "color": color,
            "aggregation": aggregation,
            "mime_type": "image/png",
            "image_base64": base64.b64encode(
                buffer.getvalue()
            ).decode("ascii"),
            "plotted_rows": int(len(frame)),
            "returned_rows": len(plotted_data),
            "data": plotted_data,
            "filters_applied": normalized_filters,
            "message": None,
        }

    except Exception as exc:
        return _error(exc)

#@tool
def answer_movie_analysis(question: str) -> dict[str, Any]:
    """Return a safe routing plan for a natural-language question."""
    try:
        normalized_question = question.casefold()
        routes: list[str] = []

        if any(
            keyword in normalized_question
            for keyword in [
                "find", "show", "movie", "film", "directed", "starring"
            ]
        ):
            routes.append("search_movies")

        if any(
            keyword in normalized_question
            for keyword in [
                "highest", "lowest", "top", "rank", "best", "worst"
            ]
        ):
            routes.append("rank_movies")

        if any(
            keyword in normalized_question
            for keyword in [
                "compare", "versus", " vs ", "by genre", "by country",
                "by company",
            ]
        ):
            routes.append("compare_segments")

        if any(
            keyword in normalized_question
            for keyword in ["trend", "over time", "by year"]
        ):
            routes.append("analyze_trends")

        if any(
            keyword in normalized_question
            for keyword in [
                "correlation", "associated", "relationship"
            ]
        ):
            routes.append("correlation_analysis")

        if any(
            keyword in normalized_question
            for keyword in [
                "summer", "holiday", "awards season", "weekend",
                "month", "quarter",
            ]
        ):
            routes.append("analyze_release_timing")

        if any(
            keyword in normalized_question
            for keyword in [
                "profit", "profitable", "roi", "revenue", "budget"
            ]
        ):
            routes.append("analyze_profitability")

        if not routes:
            routes = [
                "get_dataset_schema",
                "filter_movies",
                "aggregate_movies",
            ]

        return {
            "status": "ok",
            "question": question,
            "recommended_tools": list(dict.fromkeys(routes)),
            "data": [],
            "safety": (
                "Use structured tools only; do not generate or execute "
                "arbitrary dataframe code."
            ),
            "message": None,
        }

    except Exception as exc:
>>>>>>> 4816cd2586d4e964e8ac5abc65d2d684bae13fa6
        return _error(exc)