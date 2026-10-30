"""作業排程助手：僅使用 Python 標準函式庫。"""
import argparse
import csv
import json
import os
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from uuid import uuid4

BASE = Path(__file__).resolve().parent


def minutes(value):
    try:
        n = Decimal(str(value)) * 60
        if not n.is_finite() or n <= 0 or n != n.to_integral_value():
            raise ValueError
        return int(n)
    except (InvalidOperation, ValueError):
        raise ValueError('時數須大於零，且換算後為整數分鐘。')


def validate(data):
    if not isinstance(data, dict) or data.get('version') != 1:
        raise ValueError('不支援的資料格式。')
    if type(data.get('daily_minutes')) is not int or not 1 <= data['daily_minutes'] <= 1440:
        raise ValueError('每日時間必須介於 1 到 1440 分鐘。')
    if not isinstance(data.get('tasks'), list):
        raise ValueError('作業資料必須是清單。')
    ids = set()
    for t in data['tasks']:
        if not isinstance(t, dict) or not isinstance(t.get('id'), str) or t['id'] in ids:
            raise ValueError('作業編號有誤或重複。')
        ids.add(t['id'])
        if not isinstance(t.get('title'), str) or not t['title'].strip():
            raise ValueError('作業名稱不可空白。')
        date.fromisoformat(t['due'])
        if type(t.get('remaining')) is not int or t['remaining'] < 0:
            raise ValueError('剩餘時間須為非負整數。')
    return data


def load(path):
    if not path.exists():
        return {'version': 1, 'daily_minutes': 120, 'tasks': []}
    return validate(json.loads(path.read_text(encoding='utf-8')))


def save(path, data):
    validate(data)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(temporary, path)


def schedule(data, start=None, days=14):
    """可拆分任務的最早期限優先排程；截止日期當天也可工作。"""
    validate(data)
    if not 1 <= days <= 366:
        raise ValueError('排程天數須介於 1 到 366。')
    start = start or date.today()
    tasks = sorted((dict(t) for t in data['tasks'] if t['remaining']),
                   key=lambda t: (t['due'], t['id']))
    rows = []
    for offset in range(days):
        day = start + timedelta(days=offset)
        capacity = data['daily_minutes']
        for t in tasks:
            if not capacity:
                break
            if date.fromisoformat(t['due']) < day or not t['remaining']:
                continue
            allocated = min(capacity, t['remaining'])
            rows.append((day.isoformat(), t['title'], allocated, t['due']))
            t['remaining'] -= allocated
            capacity -= allocated
    end = start + timedelta(days=days - 1)
    warnings = []
    for t in tasks:
        if t['remaining']:
            due = date.fromisoformat(t['due'])
            status = '已逾期，請重新設定期限' if due < start else (
                '期限前時間不足' if due <= end else '超出本次排程範圍，尚未判定是否來得及')
            warnings.append(f"{t['title']}：{status}；未排入 {t['remaining']} 分鐘")
    return rows, warnings


def display(rows, warnings):
    print('\n日期         分鐘  作業（截止日）')
    for day, title, amount, due in rows:
        print(f'{day}  {amount:4}  {title}（{due}）')
    if not rows:
        print('沒有可安排的工作。')
    for warning in warnings:
        print('提醒：' + warning)


def demo_data(today=None):
    today = today or date.today()
    return {'version': 1, 'daily_minutes': 120, 'tasks': [
        {'id': str(i), 'title': title, 'due': (today + timedelta(days=offset)).isoformat(),
         'remaining': amount}
        for i, (title, offset, amount) in enumerate([
            ('數位邏輯作業', 0, 180), ('Python 專案實作', 2, 240),
            ('作業系統複習', 4, 120)], 1)]}


def choose(data):
    for i, t in enumerate(data['tasks'], 1):
        print(f"{i}. {t['title']}｜期限 {t['due']}｜剩餘 {t['remaining']} 分鐘")
    if not data['tasks']:
        raise ValueError('目前沒有作業。')
    index = int(input('選擇作業序號：')) - 1
    if not 0 <= index < len(data['tasks']):
        raise ValueError('序號不在範圍內。')
    return data['tasks'][index]


def menu(path):
    data = load(path)
    while True:
        print('\n=== Study Planner 作業排程助手 ===')
        print('1 新增作業  2 查看作業  3 記錄進度  4 修改期限')
        print('5 設定每日時數  6 產生排程  7 匯出 CSV  8 刪除作業  0 離開')
        action = input('請選擇：').strip()
        try:
            if action == '0':
                return
            if action == '1':
                title = input('作業名稱：').strip()
                if not title:
                    raise ValueError('名稱不可空白。')
                due = date.fromisoformat(input('截止日期 YYYY-MM-DD：').strip()).isoformat()
                remaining = minutes(input('預估剩餘時數（例如 1.5）：'))
                data['tasks'].append(dict(id=uuid4().hex, title=title, due=due, remaining=remaining))
            elif action == '2':
                for t in data['tasks']:
                    print(f"{t['title']}｜{t['due']}｜剩餘 {t['remaining']} 分鐘｜" +
                          ('完成' if not t['remaining'] else '進行中'))
                if not data['tasks']:
                    print('目前沒有作業。')
                continue
            elif action == '3':
                task = choose(data)
                used = minutes(input('這次完成多少時數：'))
                if used > task['remaining']:
                    raise ValueError('超過剩餘工時，請輸入剩餘時數以標記完成。')
                task['remaining'] -= used
            elif action == '4':
                task = choose(data)
                task['due'] = date.fromisoformat(input('新期限 YYYY-MM-DD：').strip()).isoformat()
            elif action == '5':
                amount = minutes(input('每天可用時數（上限 24）：'))
                if amount > 1440:
                    raise ValueError('一天最多 24 小時。')
                data['daily_minutes'] = amount
            elif action in ('6', '7'):
                days = int(input('安排幾天（1–366）：'))
                rows, warnings = schedule(data, days=days)
                display(rows, warnings)
                if action == '7':
                    target = path.parent / 'schedule.csv'
                    def safe(s):
                        return "'" + s if s.lstrip().startswith(('=', '+', '-', '@')) else s
                    with target.open('w', encoding='utf-8-sig', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(['日期', '作業', '分鐘', '截止日'])
                        writer.writerows((day, safe(title), n, due) for day, title, n, due in rows)
                        for warning in warnings:
                            writer.writerow(['提醒', safe(warning), '', ''])
                    print(f'已匯出：{target}')
                continue
            elif action == '8':
                task = choose(data)
                if input('確定刪除？輸入 y：').strip().lower() != 'y':
                    continue
                data['tasks'].remove(task)
            else:
                print('請輸入選單中的數字。')
                continue
            save(path, data)
            print('已儲存。')
        except (ValueError, OSError) as exc:
            print(f'操作未完成：{exc}')
            data = load(path)


def main():
    parser = argparse.ArgumentParser(description='作業期限與讀書排程助手')
    parser.add_argument('--demo', action='store_true', help='顯示示範，不變更個人資料')
    parser.add_argument('--data', type=Path, default=BASE / 'tasks.json', help='自訂資料檔路徑')
    args = parser.parse_args()
    try:
        if args.demo:
            display(*schedule(demo_data(), days=7))
        else:
            menu(args.data)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f'無法讀取或儲存資料：{exc}。請先備份並檢查資料檔。')
        return 1
    except (EOFError, KeyboardInterrupt):
        print('\n已結束；已儲存的資料會保留。')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
