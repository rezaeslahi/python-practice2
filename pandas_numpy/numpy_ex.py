from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

import numpy as np


# ============================================================
# 1. COLLECTION TYPES AND MEMORY BEHAVIOR
# ============================================================

def np_1_1_collection_types_and_views() -> Dict[str, object]:
    """
    Summary:
    Demonstrates that numpy arrays are np.ndarray and shows
    the difference between views (slicing) and copies (fancy indexing).
    """

    a: np.ndarray = np.array([1.0, 2.0, 3.0], dtype=np.float64)

    # Slice -> usually returns a VIEW (shares memory)
    view_slice: np.ndarray = a[1:]
    view_slice[0] = 99.0

    # Fancy indexing -> COPY
    copy_fancy: np.ndarray = a[[0, 2]]
    copy_fancy[0] = -1.0

    result: Dict[str, object] = {
        "array": a,
        "view_slice": view_slice,
        "copy_fancy": copy_fancy,
        "slice_shares_memory": np.shares_memory(a, view_slice),
        "fancy_shares_memory": np.shares_memory(a, copy_fancy),
        "type": type(a),
    }

    return result


def np_1_2_ndarray_shape_attributes() -> Dict[str, object]:
    """
    Summary:
    Shows common ndarray attributes used frequently in ML pipelines.
    """

    x: np.ndarray = np.arange(12, dtype=np.int32).reshape(3, 4)

    info: Dict[str, object] = {
        "array": x,
        "ndim": x.ndim,
        "shape": x.shape,
        "dtype": x.dtype,
        "itemsize": x.itemsize,
        "total_bytes": x.nbytes,
        "strides": x.strides,
        "is_c_contiguous": x.flags["C_CONTIGUOUS"],
    }

    return info


# ============================================================
# 2. ARRAY CREATION METHODS
# ============================================================

def np_2_1_create_large_arrays(n: int, m: int) -> Dict[str, np.ndarray]:
    """
    Summary:
    Demonstrates fast methods to create arrays.
    """

    zeros: np.ndarray = np.zeros((n, m), dtype=np.float64)
    ones: np.ndarray = np.ones((n, m), dtype=np.float64)
    full: np.ndarray = np.full((n, m), 3.14)

    # empty() is fast but values are uninitialized
    empty: np.ndarray = np.empty((n, m))

    seq: np.ndarray = np.arange(n * m)

    lin: np.ndarray = np.linspace(0.0, 1.0, n)

    return {
        "zeros": zeros,
        "ones": ones,
        "full": full,
        "empty": empty,
        "arange": seq,
        "linspace": lin,
    }


def np_2_2_random_arrays(seed: int, n: int, m: int) -> Dict[str, np.ndarray]:
    """
    Summary:
    Generates reproducible random arrays using the modern RNG API.
    """

    rng: np.random.Generator = np.random.default_rng(seed)

    normal: np.ndarray = rng.normal(0.0, 1.0, size=(n, m))
    uniform: np.ndarray = rng.uniform(-1.0, 1.0, size=(n, m))

    labels: np.ndarray = rng.integers(0, 3, size=n)

    return {
        "normal": normal,
        "uniform": uniform,
        "labels": labels,
    }


# ============================================================
# 3. INDEXING AND RESHAPING
# ============================================================

def np_3_1_indexing_patterns(x: np.ndarray) -> Dict[str, np.ndarray]:
    """
    Summary:
    Demonstrates slicing, boolean masks, and fancy indexing.
    """

    first_cols: np.ndarray = x[:, :2]

    mask: np.ndarray = x > 0
    positives: np.ndarray = x[mask]

    selected_rows: np.ndarray = x[[0, 2], :]

    return {
        "first_cols": first_cols,
        "positives": positives,
        "selected_rows": selected_rows,
    }


def np_3_2_reshape_and_transpose(x: np.ndarray) -> Dict[str, np.ndarray]:
    """
    Summary:
    Demonstrates reshape, transpose, flatten, and ravel.
    """

    reshaped: np.ndarray = x.reshape(-1, x.shape[-1])

    transposed: np.ndarray = x.T

    raveled: np.ndarray = x.ravel()

    flattened: np.ndarray = x.flatten()

    return {
        "reshaped": reshaped,
        "transposed": transposed,
        "raveled": raveled,
        "flattened": flattened,
    }


def np_3_3_broadcast_add_column_mean(x: np.ndarray) -> np.ndarray:
    """
    Summary:
    Example of broadcasting: add column means to each row.
    """

    col_mean: np.ndarray = x.mean(axis=0)

    result: np.ndarray = x + col_mean

    return result


# ============================================================
# 4. DATA TYPES
# ============================================================

def np_4_1_dtype_conversion() -> Dict[str, object]:
    """
    Summary:
    Demonstrates dtype definition, conversion, and overflow.
    """

    a: np.ndarray = np.array([255], dtype=np.uint8)

    overflow: np.ndarray = a + np.array([1], dtype=np.uint8)

    f32: np.ndarray = np.array([1.1, 2.2], dtype=np.float32)

    f64: np.ndarray = f32.astype(np.float64)

    return {
        "uint8_array": a,
        "overflow_result": overflow,
        "float32": f32.dtype,
        "float64": f64.dtype,
    }


def np_4_2_structured_array() -> np.ndarray:
    """
    Summary:
    Structured arrays allow named fields inside numpy arrays.
    """

    dt: np.dtype = np.dtype([
        ("id", np.int64),
        ("score", np.float32)
    ])

    records: np.ndarray = np.array(
        [(1, 0.9), (2, 0.1), (3, 0.7)],
        dtype=dt
    )

    return records


# ============================================================
# 5. STACKING ARRAYS
# ============================================================

def np_5_1_stack_vs_concatenate() -> Dict[str, np.ndarray]:
    """
    Summary:
    Demonstrates stack vs concatenate vs hstack vs vstack.
    """

    a: np.ndarray = np.array([1, 2, 3])
    b: np.ndarray = np.array([10, 20, 30])

    stack0: np.ndarray = np.stack([a, b], axis=0)

    stack1: np.ndarray = np.stack([a, b], axis=1)

    concat: np.ndarray = np.concatenate([a, b])

    h: np.ndarray = np.hstack([a, b])

    v: np.ndarray = np.vstack([a, b])

    return {
        "stack_axis0": stack0,
        "stack_axis1": stack1,
        "concat": concat,
        "hstack": h,
        "vstack": v,
    }


def np_5_2_build_feature_matrix(features: Sequence[np.ndarray]) -> np.ndarray:
    """
    Summary:
    Combine multiple feature vectors into a feature matrix.
    """

    X: np.ndarray = np.column_stack(features)

    return X


# ============================================================
# 6. VECTORIZATION AND EFFICIENCY
# ============================================================

def np_6_1_rowwise_l2_norm(x: np.ndarray) -> np.ndarray:
    """
    Summary:
    Compute L2 norm per row using vectorization.
    """

    squared: np.ndarray = x * x

    summed: np.ndarray = squared.sum(axis=1)

    norms: np.ndarray = np.sqrt(summed)

    return norms


def np_6_2_rowwise_dot(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Summary:
    Row-wise dot product using einsum.
    """

    result: np.ndarray = np.einsum("nd,nd->n", a, b)

    return result


def np_6_3_clip_negatives(x: np.ndarray) -> np.ndarray:
    """
    Summary:
    Replace negative values with zero.
    """

    result: np.ndarray = np.where(x < 0, 0, x)

    return result


def np_6_4_standardize_inplace(x: np.ndarray) -> np.ndarray:
    """
    Summary:
    Standardize columns in-place.
    """

    mean: np.ndarray = x.mean(axis=0)

    std: np.ndarray = x.std(axis=0)

    safe_std: np.ndarray = np.where(std == 0, 1, std)

    x -= mean

    x /= safe_std

    return x


# ============================================================
# 7. DATA PIPELINE OPERATIONS
# ============================================================

def np_7_1_impute_nan_with_mean(x: np.ndarray) -> np.ndarray:
    """
    Summary:
    Replace NaN values with column mean.
    """

    out: np.ndarray = x.copy()

    mask: np.ndarray = np.isnan(out)

    col_mean: np.ndarray = np.nanmean(out, axis=0)

    rows, cols = np.where(mask)

    out[rows, cols] = col_mean[cols]

    return out


def np_7_2_one_hot(labels: np.ndarray, num_classes: int) -> np.ndarray:
    """
    Summary:
    Convert integer labels to one-hot encoding.
    """

    n: int = labels.shape[0]

    out: np.ndarray = np.zeros((n, num_classes))

    rows: np.ndarray = np.arange(n)

    out[rows, labels] = 1

    return out


def np_7_3_train_test_split(
    X: np.ndarray,
    y: np.ndarray,
    test_ratio: float,
    seed: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Summary:
    Shuffle and split dataset.
    """

    n: int = X.shape[0]

    rng: np.random.Generator = np.random.default_rng(seed)

    idx: np.ndarray = np.arange(n)

    rng.shuffle(idx)

    test_size: int = int(n * test_ratio)

    test_idx: np.ndarray = idx[:test_size]

    train_idx: np.ndarray = idx[test_size:]

    X_train: np.ndarray = X[train_idx]
    X_test: np.ndarray = X[test_idx]

    y_train: np.ndarray = y[train_idx]
    y_test: np.ndarray = y[test_idx]

    return X_train, X_test, y_train, y_test


def np_7_4_unique_rows(x: np.ndarray) -> np.ndarray:
    """
    Summary:
    Remove duplicate rows.
    """

    unique: np.ndarray = np.unique(x, axis=0)

    return unique


def np_7_5_clip_by_percentile(x: np.ndarray, low: float, high: float) -> np.ndarray:
    """
    Summary:
    Clip values based on column percentiles.
    """

    low_val: np.ndarray = np.percentile(x, low, axis=0)

    high_val: np.ndarray = np.percentile(x, high, axis=0)

    result: np.ndarray = np.clip(x, low_val, high_val)

    return result


# ============================================================
# 8. TOP-K AND PERFORMANCE TRICKS
# ============================================================

def np_8_1_top_k_indices(scores: np.ndarray, k: int) -> np.ndarray:
    """
    Summary:
    Efficient top-k retrieval using argpartition.
    """

    n: int = scores.shape[0]

    k_eff: int = min(k, n)

    idx: np.ndarray = np.argpartition(-scores, k_eff - 1)[:k_eff]

    order: np.ndarray = np.argsort(-scores[idx])

    result: np.ndarray = idx[order]

    return result


def np_8_2_cast_to_float32(x: np.ndarray) -> np.ndarray:
    """
    Summary:
    Convert features to float32 (common for ML training).
    """

    result: np.ndarray = x.astype(np.float32)

    return result


# ============================================================
# 9. RNG INJECTION FOR REPRODUCIBILITY
# ============================================================

@dataclass(frozen=True)
class NoiseConfig:
    sigma: float


def np_9_1_add_noise(
    x: np.ndarray,
    cfg: NoiseConfig,
    rng: np.random.Generator
) -> np.ndarray:
    """
    Summary:
    Add Gaussian noise using injected RNG.
    """

    noise: np.ndarray = rng.normal(0, cfg.sigma, size=x.shape)

    result: np.ndarray = x + noise

    return result