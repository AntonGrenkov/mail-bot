

def get_parsed_body(body):
    info_dict = {}
    for string in body:
        if string.startswith('ID'):
            string = string.split(' ')
            info_dict['id'] = string[1]
            info_dict['date'] = string[3]
            info_dict['time'] = string[4].replace('\r', '')
        elif string.startswith('Курс обмена:'):
            string = string.split(': ')
            info_dict['curs'] = string[1].replace('\r', '')
        elif string.startswith('Сумма обмена:'):
            string = string.split(': ')
            exchange = string[1].replace('\r', '')
            exchange_list = exchange.split(' ')
            card_number = exchange_list[-1]
            exchange_list.pop()
            string = ' '.join(exchange_list)
            usdt, rub = string.split(' -> ')
            info_dict['usdt'] = float(usdt.split(' ')[0])
            info_dict['rub'] = float(rub.split(' ')[0])
            info_dict['sum'] = string
            info_dict['card'] = card_number
        elif string.startswith('Название банка:'):
            string = string.split(': ')
            if string[1]:
                info_dict['bank'] = string[1].replace('\r', '')
        elif string.startswith('Email:'):
            string = string.split(': ')
            info_dict['email'] = string[1].replace('\r', '')
    return info_dict


def get_text(info_dict, exchanger):
    text = (
        f'Заявка {info_dict["id"]} || {exchanger}\n'
        f'{info_dict["curs"]}\n'
        f'{info_dict["sum"]} {info_dict["card"]}\n'
    )
    if 'bank' in info_dict.keys():
        text += f'{info_dict["bank"]}\n'
    text += f'{info_dict["email"]}'
    return text
