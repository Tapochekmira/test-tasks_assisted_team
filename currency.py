def convert_to_ruble(price, currency):
    # Тут надо бы запилить парсинг для получения актуального курса.
    exchange_rate = {
        'SGD': 79.9,
    }
    return float(price) * exchange_rate[currency]
