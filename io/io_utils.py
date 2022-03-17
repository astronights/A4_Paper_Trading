import pyarrow as pa
import pyarrow.csv as csv

def df_to_csv(df, filename):
    df_pa_table = pa.Table.from_pandas(df)
    csv.write_csv(df_pa_table, filename)

def csv_to_df(filename):
    df_pa_table = csv.read_csv(filename)
    df = df_pa_table.to_pandas()
    return df