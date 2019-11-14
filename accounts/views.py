from django.shortcuts import render
from django.db import connection
from datetime import timedelta, date


def home(request):
    return render(request, 'accounts/home.html')


def display(request):
    query_string = request.GET['query_string']
    query = 'select b.isbn, TITLE, Name ' \
            'from books b, book_authors ba, author a ' \
            'where b.isbn=ba.isbn and ba.author_id=a.author_id ' \
            'and (b.isbn like \'%' + query_string + '%\' ' \
                                                    'OR title like \'%' + query_string + '%\' ' \
                                                    'OR name like \'%' + query_string + '%\')'

    print(query)
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    list_of_dict = []
    for row in rows:
        dict={}
        dict['isbn'] = row[0]
        dict['title'] = row[1]
        dict['author'] = row[2]
        list_of_dict.append(dict)

    result = {'results': list_of_dict}
    return render(request, 'accounts/result.html', result)


def borrower(request, args):
    print(args)
    print("====================")
    isbn = request.POST['isbn']
    print('attaching isbn ' + isbn)
    book = {'isbn': isbn}
    return render(request, 'accounts/borrower.html', book)


def borrow(request, isbn):
    print('lets borrow now')
    print(isbn)
    card_id = request.GET['card_id']
    print(card_id)

    is_book_available_query = 'select * from book_loans where isbn=\'' + isbn + '\' and date_in is null'
    is_user_allowed_query = 'select * from book_loans where card_id=\'' + card_id + '\' and date_in is null'
    cursor = connection.cursor()
    cursor.execute(is_book_available_query)
    result = cursor.fetchall()
    is_book_available = len(result)

    cursor.execute(is_user_allowed_query)
    result = cursor.fetchall()
    is_user_allowed = len(result)
    if is_book_available == 0:
        if is_user_allowed < 3:
            date_out = str(date.today())
            due_date = str(date.today() + timedelta(10))
            insert = 'insert into book_loans (isbn, card_id, date_out, due_date) values ' \
                 '(' + isbn + ', \'' + card_id + '\', \'' + date_out + '\', \'' + due_date + '\')'
            print(insert)
            cursor = connection.cursor()
            cursor.execute(insert)
            sub = 'Please return by ' + due_date
            msg = {'main': 'Successfully Borrowed', 'sub': sub}
            return render(request, 'accounts/success.html', msg)
        else:
            return render(request, 'accounts/failure.html', {'reason': 'Sorry this user has already borrowed 3 books'})
    else:
        return render(request, 'accounts/failure.html', {'reason': 'Sorry this book is already checked out'})


def checkin(request):
    query_string = request.GET['return_book']
    query = 'select bl.card_id, BFName, blname, bl.isbn, title, due_date, loan_id ' \
            'from book_loans bl, books b, borrower br ' \
            'where bl.isbn=b.isbn and bl.card_id=br.card_id and (bl.card_id like \'%' + query_string + '%\'' \
            ' or bfname like \'%' + query_string + '%\' or blname like \'%' + query_string + '%\' or bl.isbn like ' \
            '\'%' + query_string + '%\' or title like \'%' + query_string + '%\')  and date_in is null'

    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    list_of_dict = []
    for row in rows:
        dict = {}
        dict['card_id'] = row[0]
        dict['Fname'] = row[1]
        dict['Lname'] = row[2]
        dict['isbn'] = row[3]
        dict['title'] = row[4]
        dict['due_date'] = row[5]
        dict['loan_id'] = row[6]
        list_of_dict.append(dict)

    result = {'results': list_of_dict}
    return render(request, 'accounts/checkinresult.html', result)


def checkedin(request, args):
    print(args)
    print("-------------------------")
    loan_id = request.POST['loan']
    print(loan_id)

    date_in = str(date.today())
    update = 'update book_loans set date_in=\'' + date_in + '\' where loan_id=\'' + loan_id + '\''
    cursor = connection.cursor()
    cursor.execute(update)
    check_fine_query = 'select fine_amount from fines where loan_id=\'' + loan_id + '\''
    cursor.execute(check_fine_query)
    check_for_fine = cursor.fetchall()
    if len(check_for_fine) != 0:
        sub = 'You owe us ' + str(check_for_fine[0])
    else:
        sub = 'No pending fine'
    msg = {'main': 'Thank you for returning', 'sub': sub}
    return render(request, 'accounts/success.html', msg)


def create(request):
    print("create borrower ")
    fname = request.GET['fname']
    lname = request.GET['lname']
    ssn = request.GET['ssn']
    address = request.GET['address']
    phone = request.GET['phone']
    create_query = 'insert into borrower (ssn, bfname, blname, address, phone) values (\'' + ssn + '\',\'' + fname +\
                   '\',\'' + lname + '\',\'' + address + '\',\'' + phone + '\')'
    print(create_query)

    user_exists_query = 'select ssn from borrower where ssn=\'' + ssn + '\''
    cursor = connection.cursor()
    cursor.execute(user_exists_query)
    user_exists = len(cursor.fetchall())

    if user_exists == 0:
        cursor.execute(create_query)
        print(cursor.fetchall())
        msg = {'main': 'User created Successfully', 'sub': ''}
        return render(request, 'accounts/success.html', msg)
    else:
        return render(request, 'accounts/failure.html', {'reason': 'Sorry !! User already exists'})


def fines(request):
    get_loan_id = 'select b.loan_id, due_date, date_in, curdate() from book_loans b, fines f ' \
                  'where b.loan_id=f.loan_id and date_in > due_date and paid=FALSE UNION ' \
                  '(select b.loan_id, due_date, date_in, curdate() from book_loans b ' \
                  'where due_date < curdate() and (date_in is null))'
    cursor = connection.cursor()
    cursor.execute(get_loan_id)
    rows = cursor.fetchall()

    list_of_dict = []
    for row in rows:
        dict={}
        dict['loan_id'] = row[0]
        if row[2] is not None:
            dict['fine'] = (row[2] - row[1]).days * 0.25
        else:
            dict['fine'] = (row[3] - row[1]).days * 0.25
        print(dict)
        list_of_dict.append(dict)

    fine_records_query = 'select loan_id from fines where paid=FALSE;'
    cursor = connection.cursor()
    cursor.execute(fine_records_query)
    fine_records = cursor.fetchall()
    print(fine_records)

    list_of_loans = []
    for row in fine_records:
        list_of_loans.append(row[0])
    print(list_of_loans)

    for loan in list_of_dict:
        if loan['loan_id'] in list_of_loans:
            print('update fines')
            update_fine_query = 'update fines set fine_amount = ' + str(loan['fine']) + ' where loan_id = ' + str(loan['loan_id'])
            print(update_fine_query)
            cursor = connection.cursor()
            cursor.execute(update_fine_query)

        else:
            print('insert new fine record')
            insert_into_fines_query = 'insert into fines values (' + str(loan['loan_id']) + ', ' + str(loan['fine']) + ', FALSE)'
            print(insert_into_fines_query)
            cursor = connection.cursor()
            cursor.execute(insert_into_fines_query)
    print("Fine calculation complete")

    fines_per_user_query = 'select card_id, sum(fine_amount) as total from book_loans b, fines f where b.loan_id = f.loan_id group by card_id'
    cursor = connection.cursor()
    cursor.execute(fines_per_user_query)
    fine_records = cursor.fetchall()

    fines_per_user = []
    for row in fine_records:
        dict = {}
        dict['card_id'] = row[0]
        dict['fine'] = row[1]
        fines_per_user.append(dict)
    print(fines_per_user)

    result = {'fines': fines_per_user}
    return render(request, 'accounts/fine_display.html', result)


def payfine(request):
    card_id = request.GET['id']
    loan_list_query = 'select b.loan_id, title, fine_amount from books bo, book_loans b, fines f ' \
                'where bo.isbn=b.isbn and b.loan_id=f.loan_id and date_in is not null and paid=FALSE and card_id=\'' + card_id + '\''
    cursor = connection.cursor()
    cursor.execute(loan_list_query)
    result = cursor.fetchall()

    loan_list = []
    for row in result:
        dict = {}
        dict['card_id'] = card_id
        dict['loan_id'] = row[0]
        dict['title'] = row[1]
        dict['fine'] = row[2]
        loan_list.append(dict)

    result = {'loan_list': loan_list}
    return render(request, 'accounts/payfine.html', result)


def updatefine(request):
    loan_id = request.GET['loan_id']
    pay_fine_query = 'update fines set paid=TRUE where loan_id=' + loan_id
    cursor = connection.cursor()
    cursor.execute(pay_fine_query)

    return render(request, 'accounts/success.html', {'main': 'Thank you for paying fine.!'})
