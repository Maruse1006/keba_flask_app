import requests
import pandas as pd
from bs4 import BeautifulSoup
import pickle

class Peds:
    @staticmethod
    def scrape(horse_id_list):
        headers = {"User-Agent": "Mozilla/5.0"}
        peds_dict = {}

        for horse_id in horse_id_list:
            try:
                url = "https://db.netkeiba.com/horse/ped/" + horse_id
                response = requests.get(url, headers=headers)
                
                # BeautifulSoupでHTMLをパースしてエンコードを指定
                soup = BeautifulSoup(response.content, 'html.parser')
                html = soup.prettify()

                # pandasでデータを読み込み
                df = pd.read_html(html)[0]

                # 血統データの整形
                generations = {}
                for i in range(5):
                    if i < len(df.columns):
                        generations[f"generation_{i+1}"] = df[i]
                    df = df.drop_duplicates()

                # 各世代のデータを結合し、行方向に変換
                ped = pd.concat([generations[f"generation_{i+1}"] for i in range(5)], axis=1)
                ped.columns = [f"generation_{i+1}" for i in range(len(ped.columns))]

                peds_dict[horse_id] = ped.reset_index(drop=True)
            except Exception as e:
                print(f"{horse_id}でエラーが発生しました: {e}")
                continue

        # 全ての血統データをDataFrameに結合
        if peds_dict:
            peds_df = pd.concat([peds_dict[key] for key in peds_dict], keys=peds_dict.keys())
            print(peds_df)
        else:
            print("有効なデータがありませんでした")
            return pd.DataFrame()

        return peds_df

def load_horse_ids_from_pickle(pickle_file):
    """Pickleファイルからhorse_idを取得"""
    try:
        with open(pickle_file, 'rb') as f:
            race_results = pickle.load(f)
        horse_ids = []
        for race_id, df in race_results.items():
            horse_ids.extend(df["horse_id"].tolist())  # DataFrameのhorse_id列をリスト化
        return list(set(horse_ids))  # 重複を削除
    except Exception as e:
        print(f"Failed to load horse IDs from pickle: {e}")
        return []

if __name__ == "__main__":
    # Pickleファイルのパス
    pickle_filename = "race_results.pkl"

    # Pickleからhorse_idをロード
    horse_id_list = load_horse_ids_from_pickle(pickle_filename)
    print(f"Loaded horse IDs: {horse_id_list}")

    # horse_idを使って血統データをスクレイピング
    if horse_id_list:
        peds_data = Peds.scrape(horse_id_list)
        print(peds_data)
    else:
        print("No horse IDs found in the pickle file.")
