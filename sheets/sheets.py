from datetime import datetime, timedelta, timezone

import gspread


def get_current_time(type):
    offset = timezone(timedelta(hours=3))
    time = datetime.now(offset)
    if type == 'time':
        return time.strftime('%H:%M:%S')
    else:
        return time.strftime('%d.%m')


def fill_table(exchanger, usdt, rub):

    gc = gspread.service_account(filename='//sheets/creds.json')
    sh = gc.open_by_key('165mU4yfHciCdhkFx-Zyj5uPRyBNfsm89WBYbR5-hwY8')
    if exchanger == 'GoodBoy':
        sh = gc.open_by_key('1XxE6TlUg0J0xAbDN_gNQIwy8EQupZMNZzHvoSuDOgkA')

    worksheet_list = sh.worksheets()

    titles = []
    for worksheet in worksheet_list:
        titles.append(worksheet.title)

    current_date = get_current_time('date')

    if current_date in titles:
        worksheet = sh.worksheet(current_date)
    else:
        worksheet = sh.add_worksheet(title=current_date, rows=100, cols=4)
        worksheet.update(
            'A1:C3',
            [
                [exchanger, '', ''],
                ['', 'USDT', 'RUB'],
                ['⬇️ Время', '', '']
            ])
        formula_B2 = '=SUM(B4:B100)'
        formula_C2 = '=SUM(C4:C100)'
        worksheet.update_cell(3, 2, formula_B2)
        worksheet.update_cell(3, 3, formula_C2)
        worksheet.merge_cells('A1:C1')
        worksheet.format('A1:C100', {
            "horizontalAlignment": "CENTER",
        })
        worksheet.format('B3:C3', {
            'textFormat': {'bold': True},
            'borders': {'top': {'style': 'SOLID', 'width': 5},
                        'bottom': {'style': 'SOLID', 'width': 5},
                        'left': {'style': 'SOLID', 'width': 5},
                        'right': {'style': 'SOLID', 'width': 5}}
        })

    time = get_current_time('time')

    body = [time, usdt, rub]

    worksheet.append_row(body, table_range="A1:C1")
