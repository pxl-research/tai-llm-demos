import argparse
import sys

sys.path.append('../../')

from components.open_router.or_model_filtering import get_models
from lmarena_download import download_leaderboard, save_leaderboard_csv, SUBSET_SCORE_COLUMNS
from lmarena_scoring import LMARENA_SUBSET, normalize_lmarena_df, enrich_with_lmarena

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetches fresh OpenRouter pricing (-> or_models.csv) and an LM '
                                                  'Arena leaderboard snapshot (-> lmarena_<subset>_<date>.csv), '
                                                  'then combines them into one CSV report with a quality score '
                                                  'and cost-estimate columns alongside OpenRouter pricing.')
    parser.add_argument('--subset', default=LMARENA_SUBSET, choices=sorted(SUBSET_SCORE_COLUMNS.keys()),
                        help='Which LM Arena leaderboard to blend in.')
    parser.add_argument('--out', default='or_lmarena_report.csv', help='Filename for the combined report.')
    args = parser.parse_args()

    print('Fetching OpenRouter pricing...')
    data_models = get_models(tools_only=False,
                             image_only=False,
                             min_context=0,
                             max_completion_price=0,
                             max_prompt_price=0,
                             skip_free=True,
                             skip_experimental=False)

    print(f'Fetching LM Arena {args.subset!r} leaderboard...')
    df_leaderboard = download_leaderboard(args.subset)
    lmarena_path = save_leaderboard_csv(df_leaderboard, args.subset)
    print(f'Saved LM Arena snapshot to {lmarena_path}')

    data_models = enrich_with_lmarena(data_models, normalize_lmarena_df(df_leaderboard))
    data_models.to_csv(args.out, index=False)

    matched = data_models['lm_arena_score'].notna().sum()
    print(f'Matched {matched}/{len(data_models)} models. Saved combined report to {args.out}')
