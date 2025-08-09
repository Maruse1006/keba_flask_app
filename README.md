
### 払戻金が表示されない

## 原因
スクレイビングしたデータがフロントエンドから送られるデータと比較できるように整形出来ていない。
```
def calculate_payout(payouts, combinations, bet_type):
    """払い戻し金額を計算"""
    for payout in payouts:
        try:
            # 条件: bet_type と combinations の両方をチェック
            if payout.get('bet_type') == bet_type and any(
                sorted(combination) == sorted(
                    map(int, filter(str.isdigit, payout['combination'].replace('→', '-').replace(' ', '-').split('-')))
                )
                for combination in combinations
            ):
                # 一致した場合、該当する金額を返す
                print(f"Match found: name={bet_type}, combination={payout['combination']}")
                return payout['amount']
        except ValueError:
            # 整形時にエラーが発生した場合はスキップ
            print(f"Skipping invalid payout combination: {payout['combination']}")
            continue

    # 該当なしの場合は0を返す
    return 0g
```

