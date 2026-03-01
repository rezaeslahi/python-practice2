from __future__ import annotations
import pandas as pd
from pathlib import Path
from typing import Dict
import pandas as pd
import numpy as np
from typing import Tuple, Optional, List

# Important types you must know:

# pd.Series

# pd.DataFrame

# pd.Index

# pd.Categorical

# datetime64[ns]

# Int64 (nullable integer)

# float64

# object (string fallback)


# 1️⃣ CORE DATA TYPES OVERVIEW
# Summary:
# Demonstrates the most important pandas data structures:
# - Series: 1D labeled array
# - DataFrame: 2D labeled table
# - Index: axis labels
# - dtypes: column types



def demonstrate_core_pandas_types() -> Tuple[Dict[str, object],pd.DataFrame]:
    s = pd.Series([1.2,3.5,6.5],name="numbers",index=["a","b","c"])
    s_index = s.index
    s_types = s.dtypes
    s_type = s.dtype
    
    df = pd.DataFrame({
        "A":[1.8,2.3,4.5],
        "B":[-2,-3,-10],
        "C":["x","y","z"]
    },index=["row1","row2","row3"])
    df_index = df.index
    df_cols = df.columns
    df_types = df.dtypes
    
    
    dict = {
        "series":s,
        "DataFrame":df,
        "s_index":s_index,
        "s_types":s_types,
        "s_type":s_type,
        "df_index":df_index,
        "df_cols":df_cols,
        "df_types":df_types,
    }
    return dict,df


# 2️⃣ READ & WRITE CSV
# Summary:
# Reads a CSV into DataFrame and writes it back to disk.
# Demonstrates dtype control and date parsing.

def read_csv_file(file_path:Path,parse_dates:Optional[List[str]] = None)->pd.DataFrame:
    df = pd.read_csv(file_path,parse_dates=parse_dates)
    return df

def write_csv_file(file_path:Path,df:pd.DataFrame):
    df.to_csv(file_path,index=False)


# 3️⃣ DATE HANDLING
# Summary:
# Converts column to datetime and extracts useful features.

def convert_column_to_datetime(
    df: pd.DataFrame,
    column: str
) -> pd.DataFrame:
    df[column] = pd.to_datetime(df[column], errors="coerce")
    return df


def extract_datetime_features(
    df: pd.DataFrame,
    column: str
) -> pd.DataFrame:
    df[f"{column}_year"] = df[column].dt.year
    df[f"{column}_month"] = df[column].dt.month
    df[f"{column}_day"] = df[column].dt.day
    df[f"{column}_weekday"] = df[column].dt.weekday
    return df

# 4️⃣ BASIC EDA
# Summary:
# Quickly explores structure, summary stats and nulls.

def explore_dataframe(
    df: pd.DataFrame
) -> None:
    print("Shape:", df.shape)
    print("\nInfo:")
    print(df.info())
    print("\nDescribe:")
    print(df.describe(include="all"))
    print("\nHead:")
    print(df.head())

def decent_dict_print(dict:Dict):
    for k,v in dict.items():
        print(f"({k}: {v})")

# 5️⃣ COMMON DATA OPERATIONS
# Summary:
# Filtering, sorting, grouping, merging.

def filter_rows(
    df: pd.DataFrame,
    column: str,
    threshold: float
) -> pd.DataFrame:
    return df[df[column] > threshold]


def sort_dataframe(
    df: pd.DataFrame,
    column: str,
    ascending: bool = True
) -> pd.DataFrame:
    return df.sort_values(by=column, ascending=ascending)


def group_and_aggregate(
    df: pd.DataFrame,
    group_col: str,
    target_col: str
) -> pd.DataFrame:
    grouped: pd.DataFrame = (
        df.groupby(group_col)[target_col]
        .mean()
        .reset_index()
    )
    return grouped


def merge_dataframes(
    left: pd.DataFrame,
    right: pd.DataFrame,
    on_column: str
) -> pd.DataFrame:
    merged: pd.DataFrame = pd.merge(
        left,
        right,
        on=on_column,
        how="inner"
    )
    return merged

def get_column_types(df:pd.DataFrame)->Dict[str,str]:
    dic = {col:str(dtype) for col,dtype in df.dtypes.items()}
    return dic

# 7️⃣ DETECT MISSING VALUES
# Summary:
# Counts missing values per column and total.

def count_missing_values(
    df: pd.DataFrame
) -> pd.Series:
    missing_counts: pd.Series = df.isna().sum()
    return missing_counts


def percentage_missing(
    df: pd.DataFrame
) -> pd.Series:
    percent: pd.Series = df.isna().mean() * 100.0
    return percent

# 8️⃣ HANDLE MISSING VALUES
# Summary:
# Demonstrates drop, fill, and interpolation.

def drop_missing_rows(
    df: pd.DataFrame
) -> pd.DataFrame:
    return df.dropna()


def fill_missing_with_value(
    df: pd.DataFrame,
    value: float
) -> pd.DataFrame:
    return df.fillna(value)


def fill_numeric_with_mean(
    df: pd.DataFrame
) -> pd.DataFrame:
    numeric_cols: pd.Index = df.select_dtypes(include="number").columns
    for col in numeric_cols:
        mean_value: float = float(df[col].mean())
        df[col] = df[col].fillna(mean_value)
    return df


def forward_fill_missing(
    df: pd.DataFrame
) -> pd.DataFrame:
    return df.ffill()

# 9️⃣ FEATURE ENGINEERING & SCALING
# Summary:
# One-hot encoding and simple normalization.

def one_hot_encode(
    df: pd.DataFrame,
    column: str
) -> pd.DataFrame:
    df_encoded: pd.DataFrame = pd.get_dummies(
        df,
        columns=[column],
        drop_first=True
    )
    return df_encoded


def min_max_normalize(
    df: pd.DataFrame,
    column: str
) -> pd.DataFrame:
    min_val: float = float(df[column].min())
    max_val: float = float(df[column].max())
    df[column] = (df[column] - min_val) / (max_val - min_val)
    return df

def standard_normalize_numeric_columns(
    df: pd.DataFrame
) -> pd.DataFrame:
    numeric_cols: pd.Index = df.select_dtypes(include="number").columns

    for col in numeric_cols:
        mean_val: float = float(df[col].mean())
        std_val: float = float(df[col].std())

        if std_val != 0.0:
            df[col] = (df[col] - mean_val) / std_val

    return df

# 🔟 COMPLETE DATA PIPELINE
# Summary:
# - Reads dataset
# - Cleans
# - Handles dates
# - Handles missing values
# - Encodes categoricals
# - Normalizes numeric features
# - Returns clean feature matrix

from typing import Tuple


def prepare_dataset_for_modeling(
    path: str,
    target_column: str
) -> Tuple[pd.DataFrame, pd.Series]:

    # 1. Load
    df: pd.DataFrame = pd.read_csv(path)

    # 2. Basic cleaning
    df = df.drop_duplicates()

    # 3. Convert potential date columns automatically
    for col in df.columns:
        if "date" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="ignore")

    # 4. Separate target
    y: pd.Series = df[target_column]
    X: pd.DataFrame = df.drop(columns=[target_column])

    # 5. Handle missing numeric values
    numeric_cols: pd.Index = X.select_dtypes(include="number").columns
    for col in numeric_cols:
        mean_val: float = float(X[col].mean())
        X[col] = X[col].fillna(mean_val)

    # 6. Handle categorical columns
    categorical_cols: pd.Index = X.select_dtypes(include="object").columns
    X = pd.get_dummies(X, columns=list(categorical_cols), drop_first=True)

    # 7. Normalize numeric features
    for col in numeric_cols:
        min_val: float = float(X[col].min())
        max_val: float = float(X[col].max())
        if max_val != min_val:
            X[col] = (X[col] - min_val) / (max_val - min_val)

    return X, y


def main():
    # dic , df = demonstrate_core_pandas_types()
    # decent_dict_print(dic)
    # print(df["A"]["row1"])
    csv_file_path = Path(__file__).relative_to(Path.cwd()).parent / "sample.csv"
    # copy_csv_file_path = Path(__file__).relative_to(Path.cwd()).parent / "copy_sample.csv"
    df = read_csv_file(csv_file_path)
    # write_csv_file(copy_csv_file_path,df)
    # explore_dataframe(df)
    decent_dict_print(get_column_types(df))
    



if __name__ == "__main__":
    main()





