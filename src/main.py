from utils import get_operations_excel
from views import daypart, sort_by_date, date_list, average_spent, operation_counts

operation_date = '10.01.2018 23:03:35'
input_file_excel = "../data/operations.xlsx"


if __name__ == "__main__":
    all_operations = get_operations_excel(input_file_excel=input_file_excel)
    operations = sort_by_date(all_operations, operations_date=date_list(operation_date))

    counted_operations = dict(operation_counts(operations=operations))
    print(counted_operations)

    print(daypart(operation_date))
    print(average_spent(operations=operations, counted_operations=counted_operations))
    #print(operations)
