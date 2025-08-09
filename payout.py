from flask import Blueprint, request, jsonify
from models import db, Bets
import requests
from bs4 import BeautifulSoup

check_payout_blueprint = Blueprint('check_payout', __name__)


@check_payout_blueprint.route('/check_payout', methods=['POST'])
def check_payout():
    try:
        print("✅ Received a POST request at /check_payout")

        data = request.json
        print(f"📥 Received data: {data}")

        year = data.get('year')
        user_id = data.get('userId')
        day_count = data.get('dayCount')
        place = data.get('place')
        race = data.get('race')
        round_number = data.get('round')
        combinations = data.get('combinations')  # [["4", "1", "5"], ...]
        bet_type = data.get('name')
        bet_amounts = data.get('amounts')        # [500, 1000, ...]

        # if not (user_id and day_count and place and race and round_number and combinations and bet_type and bet_amounts):
        #     print("❌ Invalid input data")
        #     return jsonify({'success': False, 'error': 'Invalid input data'}), 400

        print("🌐 Starting scraping process...")
        payouts = scrape_payouts(year, day_count, place, race, round_number, user_id)
        print(f"✅ Scraping completed. Payouts: {payouts}")

        payout_amount, total_bet_amount, profit_or_loss = calculate_payout_with_profit(
            payouts, combinations, bet_type, bet_amounts
        )
        print(f"💰 Calculated payout amount: {payout_amount}")
        print(f"📊 Total bet amount: {total_bet_amount}")
        print(f"📈 Profit or loss: {profit_or_loss}")

        bet_entry = Bets(
            user_id=user_id,
            name=bet_type,
            amount=payout_amount,
            comment=f"収支計算: {profit_or_loss}円",
            profit_or_loss=profit_or_loss,
            date_info=day_count,
            location=place,
            race_number=race,
            round=round_number,
        )
        db.session.add(bet_entry)
        db.session.commit()
        print(f"✅ Bet successfully recorded for user_id={user_id}, profit_or_loss={profit_or_loss}")

        return jsonify({
            'success': True,
            'payout': payout_amount,
            'total_bet_amount': total_bet_amount,
            'profit_or_loss': profit_or_loss
        })

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def scrape_payouts(year, day_count, place, race, round, user_id):
    """スクレイピングして払い戻しデータを取得"""
    day_count_str = f"{int(''.join(filter(str.isdigit, day_count))):02}"
    place_str = f"{int(place):02}"
    race_str = f"{int(race):02}"
    round_str = f"{int(''.join(filter(str.isdigit, round))):02}"

    url = f"https://db.netkeiba.com/race/{year}{place_str}{round_str}{day_count_str}{race_str}/"
    print(f"🌐 Scraping URL: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "Referer": "https://db.netkeiba.com/"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch race data. Status code: {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')

    payouts = []
    payout_table = soup.find("dl", class_="pay_block")
    if not payout_table:
        print("⚠ No payout information found.")
        return payouts

    tables = payout_table.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            th = row.find("th")
            if not th:
                continue
            bet_type = th.text.strip()

            cols = row.find_all("td")
            if len(cols) >= 2:
                td_combination = cols[0].text.strip()
                td_amount = cols[1].text.strip()

                if bet_type in ["複勝", "ワイド"]:
                    combination_list = cols[0].decode_contents().replace("<br/>", "\n").split("\n")
                    amount_list = cols[1].decode_contents().replace("<br/>", "\n").split("\n")
                    for combo, amt in zip(combination_list, amount_list):
                        payouts.append({
                            'bet_type': bet_type,
                            'combination': combo.strip(),
                            'amount': int(amt.replace(',', '').replace('¥', ''))
                        })
                elif bet_type == "三連単":
                    combinations = td_combination.split("\n")
                    amounts = td_amount.split("\n")
                    for combo, amt in zip(combinations, amounts):
                        formatted_combo = combo.strip().replace(' ', '').replace('-', '→')
                        debug_combo = formatted_combo  # 矢印付きで保存
                        debug_amount = int(amt.replace(',', '').replace('¥', ''))
                        print(f"[DEBUG] 三連単の組み合わせ: {debug_combo}, 金額: {debug_amount}")
                        payouts.append({
                            'bet_type': bet_type,
                            'combination': debug_combo,
                            'amount': debug_amount
                        })
                else:
                    payouts.append({
                        'bet_type': bet_type,
                        'combination': td_combination.strip(),
                        'amount': int(td_amount.replace(',', '').replace('¥', ''))
                    })

    print(f"✅ Payouts extracted: {payouts}")
    return payouts


def calculate_payout_with_profit(payouts, combinations, bet_type, bet_amounts):
    """払い戻し金額と収支を計算"""
    filtered_payouts = [
        payout for payout in payouts if payout.get('bet_type') == bet_type
    ]

    total_payout = 0
    total_bet_amount = 0

    print(f"✅ combinations: {combinations}")

    for idx, combo_data in enumerate(combinations, start=1):
        if not bet_amounts or idx - 1 >= len(bet_amounts):
            print(f"⚠ bet_amounts[{idx-1}] が存在しません")
            continue

        if not combo_data:
            print(f"⚠ combo_data が None または空です: {combo_data}")
            continue

        bet_amount = int(bet_amounts[idx - 1])

        # 組み合わせフォーマット
        if bet_type in ["単勝", "複勝"]:
            sorted_combination = combo_data.strip().lstrip("0")
        elif bet_type == "三連単":
            sorted_combination = "→".join(combo_data).replace(" ", "")
        else:
            sorted_combination = " - ".join(sorted(combo_data))

        print(f"✅ sorted_combination: {sorted_combination}")

        total_bet_amount += bet_amount

        if not filtered_payouts:
            print(f"⚠ No matching payouts for bet_type={bet_type}")
            continue

        for payout in filtered_payouts:
            if not payout.get('combination'):
                print(f"⚠ payout['combination'] が None: {payout}")
                continue

            if bet_type in ["単勝", "複勝"]:
                payout_sorted_combination = payout['combination'].strip().lstrip("0")
            elif bet_type == "三連単":
                payout_sorted_combination = payout['combination'].replace(" ", "")
            else:
                payout_sorted_combination = " - ".join(
                    sorted(payout['combination'].replace('→', '-').replace(' ', '').split('-'))
                )

            print(f"🔍 Comparing {payout_sorted_combination} == {sorted_combination}")

            if payout_sorted_combination == sorted_combination:
                payout_contribution = payout['amount'] * (bet_amount / 100)
                print(f"🎯 Match! Adding payout {payout_contribution}")
                total_payout += payout_contribution

    profit_or_loss = total_payout - total_bet_amount
    print(f"[DEBUG] Total payout: {total_payout}, Total bet amount: {total_bet_amount}, Profit or loss: {profit_or_loss}")

    return total_payout, total_bet_amount, profit_or_loss
