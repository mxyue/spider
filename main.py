from src.service import stock_service

# stock_service.get_stocks(stock_service.upsert_all)
# stock_service.print_growth_count()

for page in range(1, 10):
    stock_service.get_growth_list(page)

stock_service.save_all_basic_info()

# stock_service.save_basic_info('300466')
