import argparse
from datetime import date

import pandas as pd

DATASET_BASE_URL = 'https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/main'

# subset -> name of the column holding the leaderboard score in that subset's parquet files.
# (most arenas publish Bradley-Terry "rating"; the agent arena publishes an IPS "score" instead.)
SUBSET_SCORE_COLUMNS = {
    'text': 'rating',
    'text_style_control': 'rating',
    'webdev': 'rating',
    'vision': 'rating',
    'vision_style_control': 'rating',
    'search': 'rating',
    'search_style_control': 'rating',
    'document': 'rating',
    'document_style_control': 'rating',
    'agent': 'score',
}


def download_leaderboard(subset, category='overall'):
    score_column = SUBSET_SCORE_COLUMNS[subset]
    url = f'{DATASET_BASE_URL}/{subset}/latest-00000-of-00001.parquet'

    df_leaderboard = pd.read_parquet(url)
    df_leaderboard = df_leaderboard[df_leaderboard['category'] == category]
    if df_leaderboard.empty:
        raise ValueError(f"No rows found for category={category!r} in subset={subset!r} "
                         f"-- check for a typo in --category.")

    df_leaderboard = df_leaderboard.rename(columns={score_column: 'score'})
    df_leaderboard['score'] = df_leaderboard['score'].round(2)

    return df_leaderboard[['model_name', 'organization', 'score', 'rank', 'leaderboard_publish_date']]


def save_leaderboard_csv(df_leaderboard, subset, out_dir='.'):
    """Saves a leaderboard DataFrame using the lmarena_<subset>_<date>.csv naming convention
    that load_lmarena_scores() (in lmarena_scoring.py) looks for. Returns the path written."""
    filename = f'lmarena_{subset}_{date.today().strftime("%y%m%d")}.csv'
    out_path = f'{out_dir}/{filename}'
    df_leaderboard.to_csv(out_path, sep=';', index=False)
    return out_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download an LMArena leaderboard snapshot from the official '
                                                  'Hugging Face dataset (lmarena-ai/leaderboard-dataset).')
    parser.add_argument('--subset', default='text_style_control', choices=sorted(SUBSET_SCORE_COLUMNS.keys()),
                        help='Which arena leaderboard to download.')
    parser.add_argument('--category', default='overall',
                        help="Category within the subset to keep (default: 'overall').")
    parser.add_argument('--out-dir', default='.', help='Folder to write the CSV into.')
    args = parser.parse_args()

    df_result = download_leaderboard(args.subset, args.category)
    print(f'Downloaded {len(df_result)} models for subset={args.subset!r}, category={args.category!r}.')

    out_path = save_leaderboard_csv(df_result, args.subset, args.out_dir)
    print(f'Saved to {out_path}')
